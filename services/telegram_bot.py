import os
import logging
import platform
from functools import wraps
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from config import Config
from services.renderer import renderer
from services.meta_api import meta_api
from services.gemini_service import gemini_service
from services.storage_service import storage_service

logger = logging.getLogger(__name__)

# Versão do deploy gerada automaticamente a partir do commit do Git
BOT_VERSION = f"sha-{os.getenv('COMMIT_SHA', 'dev')[:7]}"

# Armazenamento em memória dos posts pendentes de aprovação
PENDING_POSTS = {}

def is_user_authorized(user_id: int | None) -> bool:
    """Verifica se o remetente da mensagem está autorizado no TELEGRAM_USER_ID"""
    if not user_id:
        return False
    authorized = Config.TELEGRAM_USER_ID
    if not authorized or str(authorized).strip() in ("", "seu_telegram_user_id_aqui"):
        logger.warning(f"Acesso negado: TELEGRAM_USER_ID não foi definido no .env (Tentativa do usuário ID: {user_id})")
        return False
    authorized_ids = [uid.strip() for uid in str(authorized).split(",") if uid.strip()]
    return str(user_id) in authorized_ids

def admin_only(func):
    """Decorator para restringir o acesso apenas a administradores autorizados"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        user_id = user.id if user else None
        
        if not is_user_authorized(user_id):
            username = f"@{user.username}" if user and user.username else f"ID {user_id}"
            logger.warning(f"Acesso não autorizado bloqueado: {username} (ID: {user_id})")
            
            if update.callback_query:
                await update.callback_query.answer("⛔ Acesso não autorizado.", show_alert=True)
            elif update.message:
                await update.message.reply_text(
                    "⛔ *Acesso Restrito.*\nEste bot é de uso privado da administração.",
                    parse_mode="Markdown"
                )
            return
            
        return await func(update, context, *args, **kwargs)
    return wrapper

def format_trecho_caption(data: dict) -> str:
    """Gera a legenda formatada para o Alerta de Trecho"""
    return (
        f"🚨 ALERTA DE EMISSÃO: {data.get('origem_iata', 'GRU')} ✈️ {data.get('destino_iata', 'CDG')}\n\n"
        f"Classe: {data.get('classe', 'Executiva')}\n"
        f"Companhia Operadora: {data.get('companhia', 'LATAM Airlines')}\n"
        f"Programa: {data.get('programa', 'LATAM Pass')}\n\n"
        f"💰 CUSTO POR TRECHO:\n"
        f"• Milhas: {data.get('milhas', '45.000')} milhas\n"
        f"• Taxas: R$ {data.get('taxas', '250,00')}\n\n"
        f"📅 DATAS ENCONTRADAS:\n"
        f"{data.get('datas', 'Outubro a Novembro/2026')}\n\n"
        f"⚠️ Dica rápida: Disponibilidade sujeita à alteração rápida pelos programas. Encontrou? Emita imediatamente.\n\n"
        f"#passageiro100milhas #milhas #viagem #passagemaerea #promocao"
    )

def format_promo_caption(data: dict) -> str:
    """Gera a legenda formatada para o Informativo de Promoção"""
    return (
        f"🔥 PROMOÇÃO: {data.get('origem_programa', 'LIVELO')} ➔ {data.get('destino_programa', 'LATAM PASS')}\n\n"
        f"Bônus máximo: até {data.get('bonus_maximo', '100%')}\n"
        f"Validade: {data.get('data_validade', 'até 15 de Outubro')}\n\n"
        f"📌 REGRAS BÁSICAS:\n"
        f"• {data.get('bonus_clube', '100%')} para assinantes do Clube\n"
        f"• {data.get('bonus_geral', '50%')} para demais clientes\n"
        f"• Transferência mínima: {data.get('min_transferencia', '10.000 pontos')}\n\n"
        f"💡 ANÁLISE DO PASSAGEIRO:\n"
        f"Veredito: {data.get('veredito', 'EXCELENTE')}. Excelente oportunidade para potencializar o acúmulo de milhas.\n\n"
        f"🔗 Link oficial e regulamento nos stories!\n\n"
        f"#passageiro100milhas #milhas #pontos #livelo #latampass #promocao"
    )

@admin_only
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        f"✈️ *Painel Passageiro 100 Milhas* (`{BOT_VERSION}`)\n\n"
        "Envie uma imagem ou um texto para criar o post automaticamente com o Google Gemini:\n\n"
        "📸 *Envie um Print:* Foto da passagem ou banner da promoção.\n"
        "✍️ *Envie um Texto:* Cole o texto da promoção ou os dados do voo.\n\n"
        "*Comandos disponíveis:*\n"
        "🔹 `/status` - Status operacional do sistema\n"
        "🔹 `/trecho` - Gerar Alerta de Trecho (Exemplo)\n"
        "🔹 `/promo` - Gerar Informativo de Promoção (Exemplo)\n"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

@admin_only
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Exibe o status operacional do bot e das integrações sem expor dados sensíveis"""
    gemini_ok = bool(Config.GEMINI_API_KEY and len(Config.GEMINI_API_KEY) > 10)
    blob_ok = bool(Config.AZURE_STORAGE_CONNECTION_STRING)
    meta_configured = meta_api.is_configured()
    ig_ok = bool(meta_api.get_instagram_business_account_id()) if meta_configured else False

    gemini_status = "✅ Operacional" if gemini_ok else "❌ Não configurada"
    blob_status = "✅ Operacional" if blob_ok else "❌ Não configurada"
    
    if ig_ok:
        meta_status = "✅ Conectado (Instagram & Facebook)"
    elif meta_configured:
        meta_status = "⚠️ Token ativo (conta não vinculada)"
    else:
        meta_status = "⚠️ Modo Simulação"

    status_msg = (
        f"📊 *STATUS DO SISTEMA*\n\n"
        f"🏷️ *Versão:* `{BOT_VERSION}`\n"
        f"🐍 *Runtime:* `Python {platform.python_version()}`\n"
        f"🤖 *Extração IA:* {gemini_status}\n"
        f"☁️ *Armazenamento Nuvem:* {blob_status}\n"
        f"📱 *Redes Sociais:* {meta_status}\n"
        f"🛡️ *Controle de Acesso:* Ativo"
    )
    await update.message.reply_text(status_msg, parse_mode="Markdown")

@admin_only
async def trecho_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gera um post de demonstração de Trecho com aprovação inline"""
    await update.message.reply_text("⏳ Processando e renderizando o post de Trecho...")
    
    data = {
        "origem_iata": "GRU",
        "origem_cidade": "São Paulo",
        "destino_iata": "CDG",
        "destino_cidade": "Paris",
        "classe": "CLASSE EXECUTIVA",
        "programa": "LATAM PASS",
        "milhas": "45.000",
        "taxas": "250,00",
        "companhia": "LATAM Airlines",
        "datas": "Outubro a Novembro/2026",
    }
    await _render_and_send_preview(update, data, "trecho")

@admin_only
async def promo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gera um post de demonstração de Promoção com aprovação inline"""
    await update.message.reply_text("⏳ Processando e renderizando o post de Promoção...")
    
    data = {
        "origem_programa": "LIVELO",
        "destino_programa": "LATAM PASS",
        "bonus_maximo": "100%",
        "bonus_clube": "100% de Bônus",
        "bonus_geral": "50% de Bônus",
        "min_transferencia": "10.000 pontos",
        "validade_pontos": "24 meses",
        "veredito": "EXCELENTE",
        "data_validade": "15 de Outubro"
    }
    await _render_and_send_preview(update, data, "promo")

async def _render_and_send_preview(update: Update, data: dict, tipo: str):
    """Renderiza a imagem correspondente e envia para prévia com botões inline"""
    try:
        if tipo == "promo":
            image_path = await renderer.render_promo(data)
            caption = format_promo_caption(data)
        else:
            image_path = await renderer.render_trecho(data)
            caption = format_trecho_caption(data)

        post_id = f"post_{os.path.basename(image_path)}"
        PENDING_POSTS[post_id] = {
            "image_path": image_path,
            "caption": caption,
            "data": data,
            "tipo": tipo
        }

        keyboard = [
            [
                InlineKeyboardButton("🚀 Confirmar e Publicar", callback_data=f"pub_{post_id}"),
                InlineKeyboardButton("❌ Cancelar", callback_data=f"can_{post_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        with open(image_path, 'rb') as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=f"👁️ *PRÉVIA DO POST GERADO ({tipo.upper()})*\n\n{caption}",
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
    except Exception as e:
        logger.error(f"Erro ao renderizar arte: {e}", exc_info=True)
        await update.message.reply_text(f"❌ *Erro ao renderizar imagem:* `{e}`", parse_mode="Markdown")

def _cleanup_temp_image(image_path: str | None):
    """Remove o arquivo temporário do disco após publicação ou cancelamento"""
    if image_path and os.path.exists(image_path):
        try:
            os.remove(image_path)
            logger.debug(f"Arquivo temporário removido: {image_path}")
        except Exception as e:
            logger.warning(f"Não foi possível remover arquivo temporário {image_path}: {e}")

@admin_only
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Trata os cliques nos botões inline de aprovação ou cancelamento"""
    query = update.callback_query
    await query.answer()
    
    cb_data = query.data
    action, post_id = cb_data[:4], cb_data[4:]
    
    if post_id not in PENDING_POSTS:
        await query.edit_message_caption(caption="⚠️ Este post expirou ou já foi processado.")
        return

    post_info = PENDING_POSTS[post_id]

    if action == "pub_":
        await query.edit_message_caption(caption="⏳ Fazendo upload da imagem para o Azure Blob Storage...")
        
        try:
            image_url = storage_service.upload_image(post_info["image_path"])
        except Exception as e:
            logger.error(f"Erro no upload da imagem para a nuvem: {e}")
            await query.edit_message_caption(caption=f"❌ *Erro no upload da imagem:* `{e}`", parse_mode="Markdown")
            return

        await query.edit_message_caption(caption="⏳ Imagem na nuvem. Publicando simultaneamente no Instagram e Facebook...")
        
        res = meta_api.publish_photo(image_url, post_info["caption"])
        
        if res.get("status") in ["success", "simulated"]:
            ig_id = res.get("instagram_id")
            fb_id = res.get("facebook_id")
            
            lines = ["✅ *PUBLICAÇÃO REALIZADA COM SUCESSO!*\n"]
            if ig_id:
                lines.append(f"📸 *Instagram:* [@passageiro100milhas](https://instagram.com/passageiro100milhas) (`{ig_id}`)")
            elif res.get("instagram_error"):
                lines.append(f"⚠️ *Instagram:* `{res.get('instagram_error')}`")

            if fb_id:
                lines.append(f"📘 *Facebook:* [Página Passageiro 100 Milhas](https://facebook.com/{Config.FB_PAGE_ID}) (`{fb_id}`)")
            elif res.get("facebook_error"):
                lines.append(f"⚠️ *Facebook:* `{res.get('facebook_error')}`")

            if res.get("status") == "simulated":
                lines.append("\n*(Modo Simulação)*")

            msg = "\n".join(lines)
            await query.edit_message_caption(caption=msg, parse_mode="Markdown")
        else:
            await query.edit_message_caption(caption=f"❌ *Erro ao publicar na Meta:* `{res.get('error')}`", parse_mode="Markdown")
            
        _cleanup_temp_image(post_info.get("image_path"))
        del PENDING_POSTS[post_id]

    elif action == "can_":
        await query.edit_message_caption(caption="❌ Publicação cancelada pelo administrador.")
        _cleanup_temp_image(post_info.get("image_path"))
        del PENDING_POSTS[post_id]

@admin_only
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa fotos enviadas para o bot extraindo dados via Google Gemini Vision"""
    await update.message.reply_text("🔍 Recebi sua imagem. Otimizando e analisando com o Google Gemini Vision...")
    
    try:
        photo_file = await update.message.photo[-1].get_file()
        image_bytes = await photo_file.download_as_bytearray()
        
        data, err_msg = gemini_service.extract_from_image(bytes(image_bytes))
        
        if data and isinstance(data, dict):
            tipo = data.get("tipo", "trecho")
            await update.message.reply_text(f"✨ Dados extraídos com sucesso ({tipo.upper()})! Gerando o design do post...")
            await _render_and_send_preview(update, data, tipo)
        else:
            await update.message.reply_text(
                f"⚠️ *Não foi possível extrair dados da imagem com o Gemini.*\n\n"
                f"*Detalhes do erro:* `{err_msg}`\n\n"
                "Verifique o `/status` para checar as credenciais.",
                parse_mode="Markdown"
            )
    except Exception as e:
        logger.error(f"Erro em handle_photo: {e}", exc_info=True)
        await update.message.reply_text(f"❌ *Falha no processamento da imagem:* `{e}`", parse_mode="Markdown")

@admin_only
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa mensagens de texto informando dados de voo ou promoção via Gemini"""
    user_text = update.message.text
    if not user_text or user_text.startswith("/"):
        return

    await update.message.reply_text("🤖 Analisando o texto da promoção com o Google Gemini...")
    
    try:
        data, err_msg = gemini_service.extract_from_text(user_text)
        
        if data and isinstance(data, dict):
            tipo = data.get("tipo", "promo")
            await update.message.reply_text(f"✨ Promoção identificada ({tipo.upper()})! Gerando o design do post...")
            await _render_and_send_preview(update, data, tipo)
        else:
            await update.message.reply_text(
                f"⚠️ *Não foi possível interpretar o texto.*\n\n"
                f"*Detalhes do erro:* `{err_msg}`",
                parse_mode="Markdown"
            )
    except Exception as e:
        logger.error(f"Erro em handle_text: {e}", exc_info=True)
        await update.message.reply_text(f"❌ *Falha no processamento do texto:* `{e}`", parse_mode="Markdown")

def setup_telegram_bot() -> Application:
    """Inicializa o bot do Telegram com todos os handlers e verificações"""
    token = Config.TELEGRAM_BOT_TOKEN
    if not token or token == "seu_token_telegram_aqui":
        logger.warning("TELEGRAM_BOT_TOKEN não configurado no .env")
        return None
        
    app = Application.builder().token(token).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("trecho", trecho_command))
    app.add_handler(CommandHandler("promo", promo_command))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    return app
