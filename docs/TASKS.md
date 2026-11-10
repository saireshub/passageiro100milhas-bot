# 📋 TASKS - Gestão de Progresso e Roadmap

---

## 📌 Status Atual do Projeto
- **Fase Atual:** Deploy em Produção Concluído e Validação Operacional.
- **Ambiente:** Em execução na nuvem via **Azure Container Apps** na região Mexico Central com CI/CD automatizado no GitHub Actions.

---

## 🚀 To-Do (Próximos Passos)

### Fase 1: Refinamento Visual & Templates
- [ ] Ajustar estilização fina de cores e sombras em `templates/trecho_template.html` conforme identidade visual oficial.
- [ ] Ajustar fontes e cards comparativos em `templates/promo_template.html`.
- [ ] Testar injeção de fotos dinâmicas de fundo em alta resolução para os alertas de emissão.

### Fase 2: Backend & Novas Funcionalidades
- [ ] Implementar fluxo de conversa guiada (`ConversationHandler`) passo a passo para o comando `/promo`.
- [ ] Refinar extração OCR via Google Gemini para capturas de tela dos programas Smiles e Livelo.
- [ ] Adicionar botão de "Editar dados" no teclado inline de prévia antes de confirmar a publicação.

### Fase 3: Monitoramento Contínuo
- [ ] Acompanhar métricas de consumo de CPU/Memória no painel do Azure Container Apps.
- [ ] Monitorar alertas de gastos por e-mail configurados no Azure Cost Management.

---

## ✅ Done (Concluído)

- [x] Definição de arquitetura e modelo operacional do MVP (Telegram CMS com Human-in-the-Loop).
- [x] Criação e configuração do bot Telegram via `@BotFather` e obtenção do `TELEGRAM_BOT_TOKEN`.
- [x] Estruturação modular (`services/telegram_bot.py`, `services/renderer.py`, `services/storage_service.py`, `services/meta_api.py`, `config.py`).
- [x] Criação e padronização do `Dockerfile` multi-stage com Python 3.11 e Chromium CLI.
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
