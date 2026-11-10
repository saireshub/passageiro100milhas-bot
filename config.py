import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env se existir
load_dotenv()

class Config:
    # Credenciais do Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_USER_ID: str = os.getenv("TELEGRAM_USER_ID", "")
    TELEGRAM_WEBHOOK_SECRET: str = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
    
    # Armazenamento Azure Blob (para disponibilização pública de imagens à Meta API)
    AZURE_STORAGE_CONNECTION_STRING: str = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
    AZURE_STORAGE_CONTAINER_NAME: str = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "posts")
    
    # Meta Graph API (Instagram & Facebook - suporta chaves com prefixo FB ou META)
    META_ACCESS_TOKEN: str = os.getenv("META_ACCESS_TOKEN") or os.getenv("FB_PAGE_ACCESS_TOKEN", "")
    INSTAGRAM_ACCOUNT_ID: str = os.getenv("INSTAGRAM_ACCOUNT_ID") or os.getenv("FB_PAGE_ID", "")
    
    # Inteligência Artificial / OCR
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_API_URL: str = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/ocr")
    
    # Diretórios do Sistema
    BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_DIR: str = os.path.join(BASE_DIR, "output")
    TEMPLATES_DIR: str = os.path.join(BASE_DIR, "templates")

# Garante a existência do diretório de saída
os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
