import os
import io
import re
import json
import base64
import logging
import requests
from PIL import Image
from config import Config

logger = logging.getLogger(__name__)

EXTRACTION_SYSTEM_PROMPT = """
Você é o assistente inteligente especializado em milhas e passagens aéreas do projeto 'Passageiro 100 Milhas'.
Sua missão é analisar o texto ou a imagem fornecida (print de passagem, emissão, tabela de milhas ou promoção de transferência de pontos) e extrair os dados estruturados no formato JSON.

Classifique o conteúdo em uma de duas categorias:
1) "trecho": Alerta de emissão de passagem aérea / bilhete com milhas.
2) "promo": Informativo de promoção de bônus de transferência ou acúmulo de pontos/milhas entre programas.

Retorne EXCLUSIVAMENTE um objeto JSON válido.

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
        # Modelos disponíveis em ordem de preferência
        self.models = [
            "gemini-3.5-flash",
            "gemini-3-flash-preview",
            "gemini-3.1-flash-lite-preview",
            "gemini-3.8-flash"
        ]

    def _optimize_image(self, image_bytes: bytes, max_dim: int = 1536) -> tuple[bytes, str]:
        """Redimensiona e otimiza a imagem para evitar timeouts de rede e reduzir latência"""
        try:
            img = Image.open(io.BytesIO(image_bytes))
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            # Redimensiona mantendo a proporção se ultrapassar max_dim
            if max(img.size) > max_dim:
                img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
            
            output = io.BytesIO()
            img.save(output, format="JPEG", quality=85, optimize=True)
            return output.getvalue(), "image/jpeg"
        except Exception as e:
            logger.warning(f"Não foi possível otimizar a imagem via PIL: {e}. Usando original.")
            return image_bytes, "image/jpeg"

    def _call_api(self, payload: dict) -> tuple[dict | None, str]:
        """Executa a requisição REST para a API do Gemini com fallback e retorno de diagnóstico detalhado"""
        if not self.api_key or self.api_key.strip() in ("", "sua_chave_gemini_aqui"):
            msg = "GEMINI_API_KEY não está configurada no .env"
            logger.error(msg)
            return None, msg

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }

        errors = []
        for model in self.models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            try:
                logger.info(f"Tentando extração com Gemini modelo: {model}")
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts and "text" in parts[0]:
                            text_response = parts[0]["text"].strip()
                            parsed = self._parse_json_response(text_response)
                            if parsed:
                                return parsed, ""
                            else:
                                err = f"Modelo {model} respondeu, mas falhou ao decodificar JSON."
                                errors.append(err)
                                continue
                else:
                    err = f"Modelo {model} retornou status {response.status_code}"
                    logger.warning(f"{err}: {response.text[:200]}")
                    errors.append(err)
            except requests.RequestException as e:
                safe_err = str(e).replace(self.api_key, "***") if self.api_key else str(e)
                err = f"Timeout ou falha de rede no modelo {model}: {safe_err}"
                logger.warning(err)
                errors.append(err)

        full_error = " | ".join(errors) if errors else "Nenhum modelo respondeu com sucesso."
        logger.error(f"Todos os modelos Gemini falharam: {full_error}")
        return None, full_error

    def _parse_json_response(self, text: str) -> dict | None:
        """Limpa e decodifica a resposta JSON tolerando texto ao redor ou blocos markdown"""
        if not text:
            return None

        # 1. Tentar direto
        try:
            parsed = json.loads(text.strip())
            return self._validate_and_normalize(parsed)
        except Exception:
            pass

        # 2. Procurar bloco markdown ```json ... ``` ou ``` ... ```
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if match:
            try:
                parsed = json.loads(match.group(1).strip())
                return self._validate_and_normalize(parsed)
            except Exception:
                pass

        # 3. Procurar a primeira ocorrência de { e a última de }
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                parsed = json.loads(text[start:end+1])
                return self._validate_and_normalize(parsed)
            except Exception:
                pass

        return None

    def _validate_and_normalize(self, data: dict) -> dict | None:
        """Normaliza campos e garante que haja um campo 'tipo' válido"""
        if not isinstance(data, dict):
            return None

        # Infere o tipo se não estiver presente
        if "tipo" not in data:
            if "bonus_maximo" in data or "origem_programa" in data:
                data["tipo"] = "promo"
            elif "origem_iata" in data or "destino_iata" in data or "classe" in data:
                data["tipo"] = "trecho"
            else:
                data["tipo"] = "trecho"

        return data

    def extract_from_image(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> tuple[dict | None, str]:
        """Analisa uma imagem (print de passagem/promo) com compressão prévia e resposta estruturada"""
        opt_bytes, opt_mime = self._optimize_image(image_bytes)
        b64_image = base64.b64encode(opt_bytes).decode("utf-8")
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": EXTRACTION_SYSTEM_PROMPT + "\n\nAnalise detalhadamente a imagem anexa e retorne o JSON estruturado:"},
                    {
                        "inlineData": {
                            "mimeType": opt_mime,
                            "data": b64_image
                        }
                    }
                ]
            }],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }
        return self._call_api(payload)

    def extract_from_text(self, text_content: str) -> tuple[dict | None, str]:
        """Analisa um texto bruto de promoção ou trecho e retorna dados estruturados"""
        payload = {
            "contents": [{
                "parts": [
                    {"text": EXTRACTION_SYSTEM_PROMPT + f"\n\nAnalise o seguinte texto e retorne o JSON estruturado:\n{text_content}"}
                ]
            }],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }
        return self._call_api(payload)

gemini_service = GeminiService()
