import requests
import logging
from config import Config

logger = logging.getLogger(__name__)

class OCRExtractor:
    def __init__(self):
        self.api_url = Config.DEEPSEEK_API_URL
        self.api_key = Config.DEEPSEEK_API_KEY

    def extract_text_from_bytes(self, image_bytes: bytes) -> str:
        """Envia os bytes da imagem para a API do DeepSeek/OCR para extração de texto"""
        if not self.api_key:
            logger.warning("DeepSeek API Key não configurada.")
            return ""

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/octet-stream'
        }
        try:
            response = requests.post(self.api_url, headers=headers, data=image_bytes, timeout=30)
            if response.status_code == 200:
                return response.json().get('text', '')
            else:
                logger.error(f"Erro na API OCR: Status {response.status_code} - {response.text}")
                return ""
        except Exception as e:
            logger.error(f"Exceção ao chamar serviço de OCR: {e}")
            return ""

ocr_extractor = OCRExtractor()
