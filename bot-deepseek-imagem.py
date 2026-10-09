





from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests
import io

load_dotenv()

DEEPSEEK_API_KEY = 'SUA_CHAVE_DE_API_AQUI'
DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/ocr'

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Envie uma imagem de uma passagem aérea para extrair as informações.')

def extract_text_with_deepseek(image_bytes):
    headers = {
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
        'Content-Type': 'application/octet-stream'
    }
    response = requests.post(DEEPSEEK_API_URL, headers=headers, data=image_bytes)
    if response.status_code == 200:
        return response.json().get('text', '')
    else:
        return None

def handle_image(update: Update, context: CallbackContext) -> None:
    file = update.message.photo[-1].get_file()
    image_stream = io.BytesIO()
    file.download(out=image_stream)
    image_stream.seek(0)
    
    text = extract_text_with_deepseek(image_stream.getvalue())
    
    if text:
        # Aqui você pode adicionar lógica para processar o texto e extrair as informações específicas
        update.message.reply_text(f'Texto extraído da imagem:\n{text}')
    else:
        update.message.reply_text('Não foi possível extrair texto da imagem.')

def main() -> None:
    # Substitua 'SEU_TOKEN_AQUI' pelo token do seu bot
    updater = Updater("SEU_TOKEN_AQUI")

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.photo, handle_image))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()