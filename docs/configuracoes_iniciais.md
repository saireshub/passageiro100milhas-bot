# Configurações Iniciais do Projeto

## 1. Pré-requisitos
- **Python:** Versão 3.11 ou superior.
- **Node.js / Chromium:** Para execução do Playwright em modo headless (renderização dos templates HTML/CSS).
- **Conta de Desenvolvedor Meta:** Acesso ao Meta for Developers para criar o app do Instagram Graph API.
- **Bot no Telegram:** Token de acesso gerado via `@BotFather`.

---

## 2. Instalação e Setup do Ambiente

### 2.1 Criar Ambiente Virtual (Venv)
```bash
python -m venv venv
# No Windows PowerShell:
.\venv\Scripts\Activate.ps1
```

### 2.2 Dependências Principais (Requirements)
Instalar as bibliotecas base do projeto:
```bash
pip install python-telegram-bot playwright fastapi uvicorn requests python-dotenv pydantic jinja2
playwright install chromium
```

---

## 3. Variáveis de Ambiente (`.env`)

Crie um arquivo `.env` na raiz do projeto contendo as chaves necessárias:

```env
# Telegram Bot Token (gerado pelo BotFather)
TELEGRAM_BOT_TOKEN=seu_token_telegram_aqui

# Meta Graph API (Instagram Business)
META_ACCESS_TOKEN=seu_token_longa_duracao_meta
INSTAGRAM_ACCOUNT_ID=seu_instagram_account_id

# DeepSeek OCR / Vision API (Opcional para extração de dados por imagem)
DEEPSEEK_API_KEY=sua_chave_deepseek
DEEPSEEK_API_URL=https://api.deepseek.com/v1/ocr

# Configurações de Servidor
PORT=8000
ENVIRONMENT=development
```
