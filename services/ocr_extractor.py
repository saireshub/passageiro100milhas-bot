"""
Módulo de compatibilidade para extração de dados via OCR / IA.
Redireciona para o gemini_service oficial do Google Gemini.
"""
from services.gemini_service import gemini_service

class OCRExtractor:
    def extract_text_from_bytes(self, image_bytes: bytes) -> str:
        data = gemini_service.extract_from_image(image_bytes)
        if data:
            import json
            return json.dumps(data, ensure_ascii=False, indent=2)
        return ""

ocr_extractor = OCRExtractor()
