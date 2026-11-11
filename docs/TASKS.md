# 📋 TASKS - Gestão de Progresso e Roadmap

---

## 📌 Status Atual do Projeto
- **Fase Atual:** Produção Estável com CI/CD 100% Autônomo (OIDC + Python 3.12).
- **Ambiente:** Em execução contínua na nuvem via **Azure Container Apps** (Mexico Central), realizando extração multimodal com Google Gemini, renderização headless em Chromium e crossposting simultâneo no Instagram e Facebook.

---

## 🚀 To-Do (Próximos Passos)

### Fase 1: Refinamento Visual & Templates
- [ ] Ajustar estilização fina de cores e sombras em `templates/trecho_template.html` conforme identidade visual oficial.
- [ ] Ajustar fontes e cards comparativos em `templates/promo_template.html`.

### Fase 2: Backend & Novas Funcionalidades
- [ ] Implementar fluxo de conversa guiada (`ConversationHandler`) passo a passo para o comando `/promo`.
- [ ] Refinar extração OCR via Google Gemini para capturas de tela dos programas Smiles e Livelo.
- [ ] Adicionar botão de "Editar dados" no teclado inline de prévia antes de confirmar a publicação.
- [ ] Provisionar banco PostgreSQL (Azure Database for PostgreSQL Flexible Server na cota gratuita de 12 meses, com migração planejada para Supabase/VPS) para persistir o histórico de posts publicados.

### Fase 3: Monitoramento Contínuo
- [ ] Acompanhar métricas de consumo de CPU/Memória no painel do Azure Container Apps.
- [ ] Monitorar alertas de gastos por e-mail configurados no Azure Cost Management.

---

## ✅ Done (Concluído)

- [x] Definição de arquitetura e modelo operacional do MVP (Telegram CMS com Human-in-the-Loop).
- [x] Criação e configuração do bot Telegram via `@BotFather` e obtenção do `TELEGRAM_BOT_TOKEN`.
- [x] Estruturação modular (`services/telegram_bot.py`, `services/gemini_service.py`, `services/renderer.py`, `services/storage_service.py`, `services/meta_api.py`, `config.py`).
- [x] Criação e padronização do `Dockerfile` multi-stage com Python 3.12 e Chromium CLI.
- [x] Implementação da trava de segurança por `TELEGRAM_USER_ID` com decorator `@admin_only`.
- [x] Criação do serviço `services/storage_service.py` com integração ao Azure Blob Storage e geração de SAS URLs de 24h para a Meta Graph API.
- [x] Refinamento da verificação de status do Media Container na Meta Graph API com polling ativo (`status_code == 'FINISHED'`).
- [x] Provisionamento do grupo de recursos `rg-passageiro100milhas-mx` no Mexico Central.
- [x] Provisionamento da Conta de Armazenamento `stpassageiro100milhas` com container `passageiro100milhasbot`.
- [x] Provisionamento do Azure Container Registry (ACR) `crpassageiro100milhas`.
- [x] Provisionamento do Azure Container Apps `app-passageiro100milhas` (0.5 vCPU, 1.0 GiB RAM, Ingress desabilitado).
- [x] Configuração da esteira de CI/CD automatizada no GitHub Actions (`.github/workflows/deploy.yml`).
- [x] Injeção segura de variáveis de ambiente no Container App e início da execução contínua 24/7.
- [x] Remoção do script legado `bot-deepseek-imagem.py` e descontinuação do DeepSeek em favor do Google Gemini.
- [x] Criação do serviço `services/gemini_service.py` com extração multimodal (suporte para prints de voos e textos de promoções).
- [x] Integração de handlers no `services/telegram_bot.py` para fotos e mensagens de texto com prévia e aprovação inline.
- [x] Otimização e compressão de imagens via Pillow, retorno forçado em JSON puro (`responseMimeType`) e comando `/status`.
- [x] Auto-resolução da conta do Instagram Business (@passageiro100milhas) e crossposting simultâneo para Instagram Feed e Página do Facebook.
- [x] Correção do Chromium no Docker com `--user-data-dir` temporário em `/tmp` e `HOME=/home/appuser`.
- [x] Automação oficial de tags Docker via `docker/metadata-action` com SHA do Git e cache BuildKit (`type=gha`).
- [x] Atualização da imagem base do Dockerfile para Python 3.12 slim.
- [x] Configuração de Continuous Deployment (CD) 100% autônomo com Azure Managed Identity e OIDC (`id-github-passageiro100milhas`).
- [x] Revisão geral, limpeza de arquivos e dependências não utilizadas (`playwright`, `fastapi`, `uvicorn`, `ocr_extractor.py`, `output/test_headless.png`).
- [x] Hardening e higiene: ativação de `autoescape=True` no Jinja2 e limpeza automática de arquivos `.png` temporários após postagem/cancelamento.
- [x] Sincronização completa da documentação oficial do projeto (`ARCHITECTURE.md`, `MEMORY.md`, `SECURITY.md`, `TASKS.md`).
- [x] Hardening de privacidade e logs: remoção de dados sensíveis do `/status`, resposta minimalista a não autorizados e envio de chaves API apenas via HTTP headers (`x-goog-api-key` e `Bearer`).
- [x] Injeção dinâmica e rotação sequencial (1→7→1) de fotos de fundo otimizadas (`bg_01.jpg` a `bg_07.jpg`, 1080x1350px) em `trecho_template.html` com persistência no Azure Blob Storage.
