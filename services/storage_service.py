import os
import logging
from datetime import datetime, timedelta, timezone
from config import Config

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        self.connection_string = Config.AZURE_STORAGE_CONNECTION_STRING
        self.container_name = Config.AZURE_STORAGE_CONTAINER_NAME or "posts"
        self._blob_service_client = None

    @property
    def is_configured(self) -> bool:
        """Verifica se a conexão com o Azure Storage está configurada"""
        return bool(self.connection_string and not self.connection_string.startswith("sua_"))

    def _get_client(self):
        """Inicializa e retorna o cliente do Azure Blob Storage sob demanda"""
        if self._blob_service_client is None and self.is_configured:
            try:
                from azure.storage.blob import BlobServiceClient
                self._blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
                # Garante que o container exista
                container_client = self._blob_service_client.get_container_client(self.container_name)
                if not container_client.exists():
                    logger.info(f"Container '{self.container_name}' não existia no Azure Blob. Criando container...")
                    container_client.create_container()
            except Exception as e:
                logger.error(f"Erro ao inicializar Azure Blob Storage Client: {e}")
                self._blob_service_client = None
        return self._blob_service_client

    def upload_image(self, file_path: str, custom_blob_name: str | None = None) -> str:
        """
        Faz upload de uma imagem para o Azure Blob Storage e gera uma URL pública
        com token SAS (Shared Access Signature) de leitura válido por 24 horas.
        
        A Meta Graph API utiliza essa URL para fazer o download da imagem ao criar o container.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo de imagem não encontrado para upload: {file_path}")

        blob_name = custom_blob_name or os.path.basename(file_path)

        client = self._get_client()
        if not client:
            logger.warning("AZURE_STORAGE_CONNECTION_STRING não configurado no .env. Gerando URL mock para simulação.")
            return f"https://mockstorage.blob.core.windows.net/{self.container_name}/{blob_name}"

        try:
            from azure.storage.blob import BlobSasPermissions, ContentSettings, generate_blob_sas

            blob_client = client.get_blob_client(container=self.container_name, blob=blob_name)

            # Upload com cabeçalho de tipo de conteúdo adequado
            with open(file_path, "rb") as data:
                blob_client.upload_blob(
                    data,
                    overwrite=True,
                    content_settings=ContentSettings(content_type="image/png")
                )
            logger.info(f"Upload concluído no Azure Blob: {blob_name}")

            # Geração de token SAS temporário (24h) com permissão de leitura
            # Permite que a Meta acesse a imagem mesmo que o container seja privado na Azure
            sas_token = generate_blob_sas(
                account_name=client.account_name,
                container_name=self.container_name,
                blob_name=blob_name,
                account_key=client.credential.account_key,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.now(timezone.utc) + timedelta(hours=24)
            )

            public_url = f"{blob_client.url}?{sas_token}"
            logger.info(f"URL pública temporária gerada para Meta API: {blob_client.url} (com SAS 24h)")
            return public_url

        except Exception as e:
            logger.error(f"Falha ao realizar upload para o Azure Blob Storage: {e}")
            raise e

    def get_state_value(self, blob_name: str) -> str | None:
        """Lê um valor de estado persistente no Azure Blob Storage"""
        client = self._get_client()
        if not client:
            return None
        try:
            blob_client = client.get_blob_client(container=self.container_name, blob=blob_name)
            if not blob_client.exists():
                return None
            return blob_client.download_blob().readall().decode("utf-8").strip()
        except Exception as e:
            logger.warning(f"Não foi possível ler estado '{blob_name}' no Blob Storage: {e}")
            return None

    def set_state_value(self, blob_name: str, value: str) -> bool:
        """Salva um valor de estado persistente no Azure Blob Storage"""
        client = self._get_client()
        if not client:
            return False
        try:
            blob_client = client.get_blob_client(container=self.container_name, blob=blob_name)
            blob_client.upload_blob(value.encode("utf-8"), overwrite=True)
            return True
        except Exception as e:
            logger.warning(f"Não foi possível salvar estado '{blob_name}' no Blob Storage: {e}")
            return False

storage_service = StorageService()

