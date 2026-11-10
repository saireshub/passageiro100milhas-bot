import requests
import time
import logging
from config import Config

logger = logging.getLogger(__name__)

class MetaGraphAPI:
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v19.0"
        self._resolved_ig_id = None

    @property
    def access_token(self) -> str:
        return Config.META_ACCESS_TOKEN

    @property
    def configured_id(self) -> str:
        return Config.INSTAGRAM_ACCOUNT_ID

    def get_instagram_business_account_id(self) -> str | None:
        """
        Garante a obtenção do ID da conta do Instagram Business (@passageiro100milhas).
        Se o ID configurado for o ID da Página do Facebook, busca automaticamente
        a conta de Instagram vinculada através da Graph API.
        """
        if self._resolved_ig_id:
            return self._resolved_ig_id

        target_id = self.configured_id
        if not target_id or not self.access_token:
            return None

        # 1. Verifica se o ID configurado já é diretamente a conta do Instagram
        try:
            test_url = f"{self.base_url}/{target_id}"
            params = {
                "fields": "id,username,instagram_business_account",
                "access_token": self.access_token
            }
            res = requests.get(test_url, params=params, timeout=15)
            if res.status_code == 200:
                data = res.json()
                # Se for uma Página do Facebook com Instagram vinculado
                if "instagram_business_account" in data and "id" in data["instagram_business_account"]:
                    ig_id = data["instagram_business_account"]["id"]
                    logger.info(f"Instagram Business Account descoberto automaticamente a partir da Página: {ig_id}")
                    self._resolved_ig_id = ig_id
                    return ig_id
                elif "username" in data:
                    logger.info(f"Conta do Instagram confirmada: @{data.get('username')} (ID: {target_id})")
                    self._resolved_ig_id = target_id
                    return target_id
        except Exception as e:
            logger.warning(f"Erro ao verificar ID da Meta: {e}")

        # Se não conseguiu resolver dinamicamente, usa o ID configurado
        return target_id

    def is_configured(self) -> bool:
        return bool(
            self.access_token
            and self.configured_id
            and not self.access_token.startswith("seu_")
            and not self.configured_id.startswith("seu_")
        )

    def publish_photo(self, image_url: str, caption: str) -> dict:
        """
        Realiza o fluxo completo de publicação no Instagram Graph API:
        1. Identifica a conta Instagram Business vinculada (@passageiro100milhas)
        2. POST /{ig-account-id}/media (Cria o Container de Mídia a partir da image_url)
        3. Aguarda processamento do container (polling status_code == 'FINISHED')
        4. POST /{ig-account-id}/media_publish (Publica o post no feed do Instagram)
        """
        if not self.is_configured():
            logger.warning("Credenciais da Meta API não configuradas. Simulando publicação.")
            return {
                "status": "simulated",
                "id": "simulated_post_123",
                "message": "Modo de simulação ativado (Credenciais da Meta ausentes ou padrão)"
            }

        ig_account_id = self.get_instagram_business_account_id()
        if not ig_account_id:
            return {
                "status": "error",
                "error": "Não foi possível identificar a conta do Instagram Business vinculada."
            }

        try:
            # 1. Criação do Container de Mídia no Instagram
            container_url = f"{self.base_url}/{ig_account_id}/media"
            payload = {
                "image_url": image_url,
                "caption": caption,
                "access_token": self.access_token
            }
            logger.info(f"Enviando requisição de criação de container para Instagram ID {ig_account_id}...")
            res = requests.post(container_url, data=payload, timeout=30)
            res_data = res.json()

            if "id" not in res_data:
                logger.error(f"Erro ao criar container no Instagram: {res_data}")
                return {
                    "status": "error",
                    "error": f"Erro ao criar container no Instagram: {res_data}"
                }

            creation_id = res_data["id"]
            logger.info(f"Container de mídia criado com ID: {creation_id}")

            # 2. Verificação de status do container (polling de prontidão)
            status_url = f"{self.base_url}/{creation_id}"
            status_params = {
                "fields": "status_code",
                "access_token": self.access_token
            }
            
            is_ready = False
            for attempt in range(1, 15):
                time.sleep(3)
                status_res = requests.get(status_url, params=status_params, timeout=15)
                status_data = status_res.json()
                status_code = status_data.get("status_code")
                
                logger.info(f"Checagem do container {creation_id} (Tentativa {attempt}/15): {status_code or 'N/A'}")

                if status_code == "FINISHED":
                    is_ready = True
                    break
                elif status_code == "ERROR":
                    return {
                        "status": "error",
                        "error": f"Falha no processamento da imagem pela Meta: {status_data}"
                    }
                elif status_code is None:
                    is_ready = True
                    break

            if not is_ready:
                logger.warning(f"Timeout aguardando status FINISHED do container {creation_id}. Tentando publicar...")

            # 3. Publicação do Container no Feed do Instagram
            publish_url = f"{self.base_url}/{ig_account_id}/media_publish"
            pub_payload = {
                "creation_id": creation_id,
                "access_token": self.access_token
            }
            pub_res = requests.post(publish_url, data=pub_payload, timeout=30)
            pub_data = pub_res.json()

            if "id" not in pub_data:
                logger.error(f"Erro ao publicar mídia no Instagram: {pub_data}")
                return {
                    "status": "error",
                    "error": f"Erro ao publicar mídia no Instagram: {pub_data}"
                }

            published_id = pub_data["id"]
            logger.info(f"Post publicado no Instagram com sucesso! ID: {published_id}")
            return {
                "status": "success",
                "id": published_id,
                "ig_account_id": ig_account_id
            }

        except Exception as e:
            logger.error(f"Exceção ao publicar no Instagram via Meta API: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }

meta_api = MetaGraphAPI()
