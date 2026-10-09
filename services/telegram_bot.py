import os
import logging
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
from services.ocr_extractor import ocr_extractor

logger = logging.getLogger(__name__)

# Armazenamento em memória dos posts pendentes de aprovação
PENDING_POSTS = {}

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
        f"Validade: até {data.get('data_validade', '15 de Outubro')}\n\n"
        f"📌 REGRAS BÁSICAS:\n"
        f"• {data.get('bonus_clube', '100%')} para assinantes do Clube\n"
        f"• {data.get('bonus_geral', '50%')} para demais clientes\n"
        f"• Transferência mínima: {data.get('min_transferencia', '10.000 pontos')}\n\n"
        f"💡 ANÁLISE DO PASSAGEIRO:\n"
        f"Veredito: {data.get('veredito', 'EXCELENTE')}. Excelente oportunidade para potencializar o acúmulo de milhas.\n\n"
        f"🔗 Link oficial e regulamento nos stories!\n\n"
        f"#passageiro100milhas #milhas #pontos #livelo #latampass #promocao"
    )

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "✈️ *Bem-vindo ao Bot Passageiro 100 Milhas!*\n\n"
        "Este bot é o seu painel de controle para criação e publicação de posts no Instagram/Facebook.\n\n"
        "*Comandos disponíveis:*\n"
        "🔹 `/trecho` - Gerar Alerta de Trecho (Ex: GRU ✈ CDG)\n"
        "🔹 `/promo` - Gerar Informativo de Promoção de Milhas\n"
        "📸 *Foto:* Envie o print de uma passagem/promoção para extração automática via OCR."
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def trecho_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gera um post de exemplo/demonstração de Trecho"""
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
    
    # 1. Renderiza a imagem PNG
    image_path = await renderer.render_trecho(data)
    caption = format_trecho_caption(data)
    
    post_id = f"post_{os.path.basename(image_path)}"
    PENDING_POSTS[post_id] = {
        "image_path": image_path,
        "caption": caption,
        "data": data
    }
    
    # 2. Cria os botões inline de aprovação
    keyboard = [
        [
            InlineKeyboardButton("🚀 Confirmar e Publicar", callback_data=f"pub_{post_id}"),
            InlineKeyboardButton("❌ Cancelar", callback_data=f"can_{post_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # 3. Envia a prévia para o Telegram
    with open(image_path, 'rb') as photo:
        await update.message.reply_photo(
            photo=photo,
            caption=f"👁️ *PRÉVIA DO POST GERADO*\n\n{caption}",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

async def promo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gera um post de exemplo/demonstração de Promoção"""
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
    
    image_path = await renderer.render_promo(data)
    caption = format_promo_caption(data)
    
    post_id = f"post_{os.path.basename(image_path)}"
    PENDING_POSTS[post_id] = {
        "image_path": image_path,
        "caption": caption,
        "data": data
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
            caption=f"👁️ *PRÉVIA DO POST GERADO*\n\n{caption}",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

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
        await query.edit_message_caption(caption="⏳ Publicando no Instagram via Meta Graph API...")
        
        # Chamada da API da Meta (se não configurada, retorna simulação)
        res = meta_api.publish_photo(post_info["image_path"], post_info["caption"])
        
        if res.get("status") in ["success", "simulated"]:
            msg = f"✅ *POST PUBLICADO COM SUCESSO!*\nID: `{res.get('id')}`"
            if res.get("status") == "simulated":
                msg += "\n\n*(Modo Simulação: Configure META_ACCESS_TOKEN no .env para publicar no Instagram real)*"
            await query.edit_message_caption(caption=msg, parse_mode="Markdown")
        else:
            await query.edit_message_caption(caption=f"❌ *Erro ao publicar:* {res.get('error')}", parse_mode="Markdown")
            
        del PENDING_POSTS[post_id]

    elif action == "can_":
        await query.edit_message_caption(caption="❌ Publicação cancelada pelo administrador.")
        del PENDING_POSTS[post_id]

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa fotos enviadas para o bot extraindo texto via OCR"""
    await update.message.reply_text("🔍 Recebi sua imagem. Analisando via OCR...")
    
    photo_file = await update.message.photo[-1].get_file()
    image_bytes = await photo_file.download_as_bytearray()
    
    extracted_text = ocr_extractor.extract_text_from_bytes(bytes(image_bytes))
    
    if extracted_text:
        await update.message.reply_text(f"📝 *Texto extraído da imagem:*\n\n`{extracted_text[:1000]}`", parse_mode="Markdown")
    else:
        await update.message.reply_text("⚠️ Não foi possível extrair dados da imagem ou a chave DEEPSEEK_API_KEY não está configurada no `.env`.")

def setup_telegram_bot() -> Application:
    """Inicializa o bot do Telegram com todos os handlers"""
    token = Config.TELEGRAM_BOT_TOKEN
    if not token or token == "seu_token_telegram_aqui":
        logger.warning("TELEGRAM_BOT_TOKEN não configurado no .env")
        return None
        
    app = Application.builder().token(token).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("trecho", trecho_command))
    app.add_handler(CommandHandler("promo", promo_command))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    return app
