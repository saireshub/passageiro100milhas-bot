import requests
import time
import logging
from config import Config

logger = logging.getLogger(__name__)

class MetaGraphAPI:
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v19.0"

    @property
    def access_token(self) -> str:
        return Config.META_ACCESS_TOKEN

    @property
    def ig_account_id(self) -> str:
        return Config.INSTAGRAM_ACCOUNT_ID

    def is_configured(self) -> bool:
        return bool(
            self.access_token
            and self.ig_account_id
            and not self.access_token.startswith("seu_")
            and not self.ig_account_id.startswith("seu_")
        )

    def publish_photo(self, image_url: str, caption: str) -> dict:
        """
        Realiza o fluxo completo de publicação no Instagram Graph API:
        1. POST /{ig-account-id}/media (Cria o Container de Mídia a partir da image_url)
        2. Aguarda processamento do container (pooling status_code == 'FINISHED')
        3. POST /{ig-account-id}/media_publish (Publica o post no feed)
        """
        if not self.is_configured():
            logger.warning("Credenciais da Meta API não configuradas. Simulando publicação.")
            return {
                "status": "simulated",
                "id": "simulated_post_123",
                "message": "Modo de simulação ativado (Credenciais da Meta ausentes ou padrão)"
            }

        try:
            # 1. Criação do Container de Mídia
            container_url = f"{self.base_url}/{self.ig_account_id}/media"
            payload = {
                "image_url": image_url,
                "caption": caption,
                "access_token": self.access_token
            }
            logger.info(f"Enviando requisição de criação de container para {container_url}...")
            res = requests.post(container_url, data=payload, timeout=30)
            res_data = res.json()

            if "id" not in res_data:
                raise Exception(f"Erro ao criar container na Meta: {res_data}")

            creation_id = res_data["id"]
            logger.info(f"Container de mídia criado com ID: {creation_id}")

            # 2. Verificação de status do container (polling de prontidão)
            # Evita o erro 2207001 (Media container is not ready)
            status_url = f"{self.base_url}/{creation_id}"
            status_params = {
                "fields": "status_code",
                "access_token": self.access_token
            }
            
            is_ready = False
            for attempt in range(1, 11):
                time.sleep(3)
                status_res = requests.get(status_url, params=status_params, timeout=15)
                status_data = status_res.json()
                status_code = status_data.get("status_code")
                
                logger.info(f"Checagem do container {creation_id} (Tentativa {attempt}/10): {status_code or 'N/A'}")

                if status_code == "FINISHED":
                    is_ready = True
                    break
                elif status_code == "ERROR":
                    raise Exception(f"Falha no processamento da imagem pela Meta: {status_data}")
                elif status_code is None:
                    # Algumas versões da API não retornam status_code para imagens simples prontas
                    is_ready = True
                    break

            if not is_ready:
                logger.warning(f"Timeout aguardando processamento do container {creation_id}. Tentando publicar mesmo assim...")

            # 3. Publicação do Container
            publish_url = f"{self.base_url}/{self.ig_account_id}/media_publish"
            pub_payload = {
                "creation_id": creation_id,
                "access_token": self.access_token
            }
            pub_res = requests.post(publish_url, data=pub_payload, timeout=30)
            pub_data = pub_res.json()

            if "id" not in pub_data:
                raise Exception(f"Erro ao publicar no Instagram: {pub_data}")

            published_id = pub_data["id"]
            logger.info(f"Post publicado com sucesso no Instagram! ID: {published_id}")
            return {"status": "success", "id": published_id}

        except Exception as e:
            logger.error(f"Falha na publicação na Meta Graph API: {e}")
            return {"status": "error", "error": str(e)}

meta_api = MetaGraphAPI()
