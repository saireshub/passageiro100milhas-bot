import os
import json
import base64
import logging
import requests
from config import Config

logger = logging.getLogger(__name__)

EXTRACTION_SYSTEM_PROMPT = """
Você é o assistente inteligente especializado em milhas e passagens aéreas do projeto 'Passageiro 100 Milhas'.
Sua missão é analisar o texto ou a imagem fornecida (print de passagem, emissão, tabela de milhas ou promoção de transferência de pontos) e extrair os dados estruturados no formato JSON.

Classifique o conteúdo em uma de duas categorias:
1) "trecho": Alerta de emissão de passagem aérea / bilhete com milhas.
2) "promo": Informativo de promoção de bônus de transferência ou acúmulo de pontos/milhas entre programas.

Retorne EXCLUSIVAMENTE um objeto JSON válido, sem texto explicativo adicional.

---
Se for "trecho", use esta estrutura:
{
  "tipo": "trecho",
  "origem_iata": "Código IATA de 3 letras da origem (ex: GRU, GIG, BSB)",
  "origem_cidade": "Nome da cidade de origem (ex: São Paulo, Rio de Janeiro)",
  "destino_iata": "Código IATA de 3 letras do destino (ex: CDG, MIA, LIS)",
  "destino_cidade": "Nome da cidade de destino (ex: Paris, Miami, Lisboa)",
  "classe": "CLASSE EXECUTIVA, CLASSE ECONÔMICA ou PREMIUM ECONOMY",
  "programa": "Programa emissor (ex: LATAM PASS, SMILES, AZUL FIDELIDADE, TAP MILES&GO, IBERIA PLUS, FLYING BLUE)",
  "milhas": "Quantidade de milhas formatada (ex: 45.000 ou 72.000)",
  "taxas": "Valor das taxas em reais (ex: 250,00 ou 380,00)",
  "companhia": "Companhia operadora (ex: LATAM Airlines, Air France, TAP)",
  "datas": "Período ou meses encontrados (ex: Outubro a Novembro/2026)"
}

---
Se for "promo", use esta estrutura:
{
  "tipo": "promo",
  "origem_programa": "Programa de origem (ex: LIVELO, ESFERA, CARTÕES CAIXA, ITAÚ)",
  "destino_programa": "Programa de destino (ex: LATAM PASS, SMILES, AZUL FIDELIDADE)",
  "bonus_maximo": "Percentual máximo de bônus (ex: 100%, 80%)",
  "bonus_clube": "Bônus para assinantes do clube (ex: 100% de Bônus)",
  "bonus_geral": "Bônus para demais clientes (ex: 50% de Bônus)",
  "min_transferencia": "Quantidade mínima de transferência (ex: 10.000 pontos)",
  "validade_pontos": "Validade dos pontos (ex: 24 meses ou Não expiram)",
  "veredito": "Avaliação curta em maiúsculas (ex: EXCELENTE, MUITO BOM, REGULAR)",
  "data_validade": "Data de término da oferta (ex: até 15 de Outubro)"
}

Caso a informação não esteja explícita na imagem/texto, deduza pelo contexto com base nos padrões do mercado de milhas brasileiro ou preencha com valor padrão coerente.
"""

class GeminiService:
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        # Lista de modelos por prioridade para fallback automático
        self.models = [
            "gemini-3.5-flash",
            "gemini-3-flash-preview",
            "gemini-3.1-flash-lite-preview",
            "gemini-3.8-flash",
            "gemini-2.5-flash"
        ]

    def _call_api(self, payload: dict) -> dict | None:
        """Executa a requisição REST para a API do Gemini com fallback entre modelos"""
        if not self.api_key or self.api_key.strip() in ("", "sua_chave_gemini_aqui"):
            logger.error("GEMINI_API_KEY não configurada no .env")
            return None

        for model in self.models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
            try:
                logger.info(f"Tentando extração com Gemini modelo: {model}")
                response = requests.post(url, json=payload, timeout=25)
                
                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts and "text" in parts[0]:
                            text_response = parts[0]["text"].strip()
                            return self._parse_json_response(text_response)
                elif response.status_code == 400:
                    logger.error(f"Erro 400 da API Gemini (Chave inválida ou payload incorreto): {response.text}")
                    # Erro de autenticação não adianta tentar outro modelo
                    break
                else:
                    logger.warning(f"Modelo {model} retornou status {response.status_code}. Tentando próximo...")
            except requests.RequestException as e:
                logger.warning(f"Timeout ou erro de conexão no modelo {model}: {e}. Tentando próximo...")

        logger.error("Todos os modelos Gemini falharam na requisição.")
        return None

    def _parse_json_response(self, text: str) -> dict | None:
        """Limpa blocos de código markdown e converte a resposta para dicionário Python"""
        try:
            cleaned = text.strip()
            if cleaned.startswith("```"):
                lines = cleaned.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                cleaned = "\n".join(lines).strip()
            
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict) and "tipo" in parsed:
                return parsed
            logger.error(f"Resposta JSON do Gemini não continha campo 'tipo': {parsed}")
            return None
        except Exception as e:
            logger.error(f"Falha ao decodificar JSON retornado pelo Gemini: {e}\nTexto bruto: {text}")
            return None

    def extract_from_image(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> dict | None:
        """Analisa uma imagem (print de passagem/promo) e retorna dados estruturados"""
        b64_image = base64.b64encode(image_bytes).decode("utf-8")
        payload = {
            "contents": [{
                "parts": [
                    {"text": EXTRACTION_SYSTEM_PROMPT + "\n\nAnalise esta imagem:"},
                    {
                        "inlineData": {
                            "mimeType": mime_type,
                            "data": b64_image
                        }
                    }
                ]
            }],
            "generationConfig": {
                "temperature": 0.2
            }
        }
        return self._call_api(payload)

    def extract_from_text(self, text_content: str) -> dict | None:
        """Analisa um texto bruto (mensagem de texto sobre promoção/trecho) e retorna dados estruturados"""
        payload = {
            "contents": [{
                "parts": [
                    {"text": EXTRACTION_SYSTEM_PROMPT + f"\n\nAnalise o seguinte texto:\n{text_content}"}
                ]
            }],
            "generationConfig": {
                "temperature": 0.2
            }
        }
        return self._call_api(payload)

gemini_service = GeminiService()
