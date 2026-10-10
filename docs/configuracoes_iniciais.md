# Configurações Iniciais do Projeto

## 1. Pré-requisitos
- **Python:** Versão 3.11 ou superior.
- **Chromium:** Para execução da renderização headless dos templates HTML/CSS.
- **Conta de Desenvolvedor Meta:** Acesso ao Meta for Developers para criar o app do Instagram Graph API.
- **Bot no Telegram:** Token de acesso gerado via `@BotFather`.
- **Azure for Students (Opcional para Deploy):** Conta acadêmica ativa com créditos gratuitos.

---

## 2. Instalação e Setup do Ambiente Local

### 2.1 Criar Ambiente Virtual (Venv)
```bash
python -m venv venv
# No Windows PowerShell:
.\venv\Scripts\Activate.ps1
```

### 2.2 Dependências Principais (Requirements)
Instalar as bibliotecas base do projeto:
```bash
pip install -r requirements.txt
python -m playwright install chromium
```

---

## 3. Variáveis de Ambiente (`.env`)

Crie um arquivo `.env` na raiz do projeto contendo as chaves necessárias:

```env
# Telegram Bot Token (gerado pelo BotFather)
TELEGRAM_BOT_TOKEN=seu_token_telegram_aqui
TELEGRAM_USER_ID=seu_id_telegram_aqui

# Meta Graph API (Instagram Business)
META_ACCESS_TOKEN=seu_token_longa_duracao_meta
INSTAGRAM_ACCOUNT_ID=seu_instagram_account_id

# Google Gemini / DeepSeek API (Opcional para IA e OCR)
GEMINI_API_KEY=sua_chave_gemini_aqui

# Configurações de Servidor
PORT=8000
ENVIRONMENT=development
```

---

## 4. Deploy com Docker e Docker Compose (Azure VM)

Para subir o bot 24/7 em uma VM Linux (Ubuntu) no Azure:

```bash
# 1. Clonar o repositório na VM
git clone https://github.com/saireshub/passageiro100milhas-bot.git
cd passageiro100milhas-bot

# 2. Criar o arquivo .env com suas chaves
nano .env

# 3. Subir o container em background
docker compose up -d --build

# 4. Ver logs em tempo real
docker compose logs -f
```
