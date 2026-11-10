import os
import logging
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

# Versão do deploy para rastreio no chat
BOT_VERSION = "2026.11.10-gemini-v3"

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
                    "⛔ *Acesso Restrito!*\n\n"
                    "Este bot é o painel de administração privado do *Passageiro 100 Milhas*.\n\n"
                    f"Seu ID Telegram: `{user_id}` não possui permissão de acesso.\n"
                    "Para liberar seu acesso, adicione este ID na variável `TELEGRAM_USER_ID` do arquivo `.env`.",
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
        "🔹 `/status` - Diagnóstico do sistema e variáveis de ambiente\n"
        "🔹 `/trecho` - Gerar Alerta de Trecho (Exemplo)\n"
        "🔹 `/promo` - Gerar Informativo de Promoção (Exemplo)\n"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

@admin_only
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Exibe o status do contêiner e a verificação das integrações"""
    gemini_key = Config.GEMINI_API_KEY
    gemini_status = f"✅ Ativa (`{gemini_key[:8]}...`)" if gemini_key and len(gemini_key) > 10 else "❌ Não configurada"
    
    blob_conn = Config.AZURE_STORAGE_CONNECTION_STRING
    blob_status = f"✅ Configurada (Container: `{Config.AZURE_STORAGE_CONTAINER_NAME}`)" if blob_conn else "❌ Não configurada"
    
    meta_token = Config.META_ACCESS_TOKEN
    meta_status = f"✅ Ativo (`{meta_token[:8]}...`)" if meta_token else "⚠️ Simulação"

    status_msg = (
        f"📊 *STATUS DO SISTEMA* (`{BOT_VERSION}`)\n\n"
        f"🤖 *Google Gemini:* {gemini_status}\n"
        f"☁️ *Azure Blob Storage:* {blob_status}\n"
        f"📸 *Meta Graph API:* {meta_status}\n"
        f"👤 *Admin Telegram ID:* `{Config.TELEGRAM_USER_ID}`\n"
        f"📁 *Saída de Imagens:* `{Config.OUTPUT_DIR}`"
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

        await query.edit_message_caption(caption="⏳ Imagem na nuvem. Publicando no Instagram via Meta Graph API...")
        
        res = meta_api.publish_photo(image_url, post_info["caption"])
        
        if res.get("status") in ["success", "simulated"]:
            msg = f"✅ *POST PUBLICADO COM SUCESSO!*\nID: `{res.get('id')}`"
            if res.get("status") == "simulated":
                msg += "\n\n*(Modo Simulação: Configure credenciais reais da Meta no .env para publicar no Instagram real)*"
            await query.edit_message_caption(caption=msg, parse_mode="Markdown")
        else:
            await query.edit_message_caption(caption=f"❌ *Erro ao publicar na Meta:* `{res.get('error')}`", parse_mode="Markdown")
            
        del PENDING_POSTS[post_id]

    elif action == "can_":
        await query.edit_message_caption(caption="❌ Publicação cancelada pelo administrador.")
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
