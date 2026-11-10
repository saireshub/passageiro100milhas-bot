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
    def fb_page_id(self) -> str:
        return Config.FB_PAGE_ID

    @property
    def configured_ig_id(self) -> str:
        return Config.INSTAGRAM_ACCOUNT_ID

    def get_instagram_business_account_id(self) -> str | None:
        """
        Garante a obtenção do ID da conta do Instagram Business (@passageiro100milhas).
        Se já estiver configurado como ID de Instagram válido, usa direto.
        Caso contrário, busca através da Página do Facebook vinculada.
        """
        if self._resolved_ig_id:
            return self._resolved_ig_id

        target_id = self.configured_ig_id or self.fb_page_id
        if not target_id or not self.access_token:
            return None

        # 1. Verifica se já é conta de Instagram ou busca a vinculada
        try:
            test_url = f"{self.base_url}/{target_id}"
            params = {
                "fields": "id,username,instagram_business_account",
                "access_token": self.access_token
            }
            res = requests.get(test_url, params=params, timeout=15)
            if res.status_code == 200:
                data = res.json()
                if "instagram_business_account" in data and "id" in data["instagram_business_account"]:
                    ig_id = data["instagram_business_account"]["id"]
                    logger.info(f"Instagram Business Account auto-descoberto da Página: {ig_id}")
                    self._resolved_ig_id = ig_id
                    return ig_id
                elif "username" in data:
                    self._resolved_ig_id = target_id
                    return target_id
        except Exception as e:
            logger.warning(f"Erro ao verificar ID da Meta: {e}")

        # Fallback para o ID configurado
        return target_id

    def is_configured(self) -> bool:
        return bool(
            self.access_token
            and not self.access_token.startswith("seu_")
        )

    def publish_to_instagram(self, image_url: str, caption: str) -> dict:
        """Publica a imagem no feed do Instagram Business (@passageiro100milhas)"""
        ig_account_id = self.get_instagram_business_account_id()
        if not ig_account_id:
            return {"status": "error", "error": "ID da conta do Instagram Business não localizado."}

        try:
            # 1. Criação do Container
            container_url = f"{self.base_url}/{ig_account_id}/media"
            payload = {
                "image_url": image_url,
                "caption": caption,
                "access_token": self.access_token
            }
            logger.info(f"Criando container no Instagram ({ig_account_id})...")
            res = requests.post(container_url, data=payload, timeout=30)
            res_data = res.json()

            if "id" not in res_data:
                return {"status": "error", "error": f"Erro container Instagram: {res_data}"}

            creation_id = res_data["id"]

            # 2. Polling de prontidão
            status_url = f"{self.base_url}/{creation_id}"
            status_params = {"fields": "status_code", "access_token": self.access_token}
            
            for attempt in range(1, 15):
                time.sleep(3)
                status_res = requests.get(status_url, params=status_params, timeout=15)
                status_data = status_res.json()
                status_code = status_data.get("status_code")
                if status_code == "FINISHED" or status_code is None:
                    break
                elif status_code == "ERROR":
                    return {"status": "error", "error": f"Processamento da imagem falhou no Instagram: {status_data}"}

            # 3. Publicação do Container
            publish_url = f"{self.base_url}/{ig_account_id}/media_publish"
            pub_payload = {"creation_id": creation_id, "access_token": self.access_token}
            pub_res = requests.post(publish_url, data=pub_payload, timeout=30)
            pub_data = pub_res.json()

            if "id" not in pub_data:
                return {"status": "error", "error": f"Erro media_publish Instagram: {pub_data}"}

            return {"status": "success", "id": pub_data["id"], "username": "passageiro100milhas"}

        except Exception as e:
            logger.error(f"Erro publicando no Instagram: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}

    def publish_to_facebook(self, image_url: str, caption: str) -> dict:
        """Publica a imagem diretamente na Página do Facebook (Passageiro100Milhas)"""
        page_id = self.fb_page_id
        if not page_id:
            return {"status": "error", "error": "FB_PAGE_ID não configurado."}

        try:
            url = f"{self.base_url}/{page_id}/photos"
            payload = {
                "url": image_url,
                "message": caption,
                "access_token": self.access_token
            }
            logger.info(f"Publicando foto na Página do Facebook ({page_id})...")
            res = requests.post(url, data=payload, timeout=30)
            res_data = res.json()

            if "id" not in res_data:
                logger.error(f"Erro ao publicar foto no Facebook: {res_data}")
                return {"status": "error", "error": f"Erro Facebook: {res_data}"}

            return {
                "status": "success",
                "id": res_data.get("post_id") or res_data["id"],
                "page_id": page_id
            }

        except Exception as e:
            logger.error(f"Erro publicando no Facebook: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}

    def publish_photo(self, image_url: str, caption: str) -> dict:
        """
        Publica simultaneamente no Instagram e na Página do Facebook (Crossposting)
        """
        if not self.is_configured():
            logger.warning("Credenciais da Meta API não configuradas. Simulando publicação.")
            return {
                "status": "simulated",
                "id": "simulated_post_123",
                "message": "Modo simulação"
            }

        # 1. Publica no Instagram
        ig_res = self.publish_to_instagram(image_url, caption)
        
        # 2. Publica no Facebook
        fb_res = self.publish_to_facebook(image_url, caption)

        ig_success = ig_res.get("status") == "success"
        fb_success = fb_res.get("status") == "success"

        if ig_success or fb_success:
            return {
                "status": "success",
                "instagram_id": ig_res.get("id"),
                "facebook_id": fb_res.get("id"),
                "instagram_status": ig_res.get("status"),
                "facebook_status": fb_res.get("status"),
                "instagram_error": ig_res.get("error"),
                "facebook_error": fb_res.get("error")
            }
        else:
            return {
                "status": "error",
                "error": f"Instagram: {ig_res.get('error')} | Facebook: {fb_res.get('error')}"
            }

meta_api = MetaGraphAPI()
