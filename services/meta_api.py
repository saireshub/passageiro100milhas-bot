import requests
import time
import logging
from config import Config

logger = logging.getLogger(__name__)

class MetaGraphAPI:
    def __init__(self):
        self.access_token = Config.META_ACCESS_TOKEN
        self.ig_account_id = Config.INSTAGRAM_ACCOUNT_ID
        self.base_url = "https://graph.facebook.com/v19.0"

    def publish_photo(self, image_url: str, caption: str) -> dict:
        """
        Realiza o fluxo completo de publicação no Instagram Graph API:
        1. POST /{ig-account-id}/media (Cria o Container de Mídia)
        2. Aguarda processamento
        3. POST /{ig-account-id}/media_publish (Publica a mídia)
        """
        if not self.access_token or not self.ig_account_id:
            logger.warning("Credenciais da Meta API não configuradas. Simulando publicação.")
            return {"status": "simulated", "id": "simulated_post_123", "message": "Modo de simulação ativado"}

        try:
            # 1. Criação do Container
            container_url = f"{self.base_url}/{self.ig_account_id}/media"
            payload = {
                "image_url": image_url,
                "caption": caption,
                "access_token": self.access_token
            }
            res = requests.post(container_url, data=payload)
            res_data = res.json()

            if "id" not in res_data:
                raise Exception(f"Erro ao criar container: {res_data}")

            creation_id = res_data["id"]
            logger.info(f"Container criado com ID: {creation_id}")

            # Pequena pausa para garantir que o Instagram processou a imagem
            time.sleep(5)

            # 2. Publicação do Container
            publish_url = f"{self.base_url}/{self.ig_account_id}/media_publish"
            pub_payload = {
                "creation_id": creation_id,
                "access_token": self.access_token
            }
            pub_res = requests.post(publish_url, data=pub_payload)
            pub_data = pub_res.json()

            if "id" not in pub_data:
                raise Exception(f"Erro ao publicar no Instagram: {pub_data}")

            logger.info(f"Post publicado no Instagram com ID: {pub_data['id']}")
            return {"status": "success", "id": pub_data["id"]}

        except Exception as e:
            logger.error(f"Falha na publicação na Meta Graph API: {e}")
            return {"status": "error", "error": str(e)}

meta_api = MetaGraphAPI()
