# 📋 TASKS - Gestão de Progresso e Roadmap

---

## 📌 Status Atual do Projeto
- **Fase Atual:** Finalização de Setup Operacional e Templates Visuais.
- **Ambiente:** Desenvolvimento local com preparação de deploy na Azure VM B1s via Docker Compose.

---

## 🚀 To-Do (A Fazer)

### Fase 1: Setup de Contas & Chaves Externas
- [ ] Concluir migração da conta do Instagram para perfil Profissional/Criador.
- [ ] Vincular a Página correspondente no Facebook.
- [ ] Configurar aplicativo no Meta for Developers e aprovar escopo `instagram_content_publish`.
- [ ] Gerar Token de Acesso de Longa Duração (60 dias) e preencher no `.env`.
- [ ] Obter credenciais do Azure for Students e provisionar VM `Standard_B1s` Ubuntu 24.04.

### Fase 2: Templates Visuais & Renderização
- [ ] Finalizar estilização CSS de `templates/trecho_template.html` (1080x1350px).
- [ ] Finalizar estilização CSS de `templates/promo_template.html`.
- [ ] Testar injeção de imagens de fundo dinâmicas em `templates/trecho_template.html`.

### Fase 3: Módulos de Backend & Integração
- [ ] Implementar fluxo conversacional guiado `/promo` no `services/telegram_bot.py`.
- [ ] Refinar extração OCR inteligente para prints de telas Smiles, LATAM Pass e Livelo.
- [ ] Integrar testes ponta a ponta de publicação direta na Meta Graph API com permalink de retorno.

### Fase 4: Deploy & Automação 24/7
- [ ] Conectar via SSH na VM Azure B1s e clonar o repositório.
- [ ] Configurar arquivo `.env` na VM.
- [ ] Subir containers com `docker compose up -d --build`.
- [ ] Configurar rotina periódica de limpeza de arquivos antigos em `output/`.

---

## 🔄 In Progress (Em Andamento)

- [x] Padronização completa da documentação técnica e regras de agentes no novo padrão oficial (9 arquivos).
- [ ] Validação do motor de renderização `services/renderer.py` usando Chromium CLI sem dependências restritivas no Windows.

---

## ✅ Done (Concluído)

- [x] Definição de arquitetura e modelo operacional do MVP (Telegram CMS com Human-in-the-Loop).
- [x] Avaliação técnica e seleção de provedor de hospedagem (Azure for Students VM B1s vs Render vs Oracle).
- [x] Criação do bot Telegram via `@BotFather` e obtenção do `TELEGRAM_BOT_TOKEN`.
- [x] Estruturação modular inicial (`services/telegram_bot.py`, `services/renderer.py`, `services/meta_api.py`, `config.py`).
- [x] Criação do `Dockerfile` e `docker-compose.yml` para suporte a Python e Chromium.
- [x] Elaboração das regras do sistema e convenção de commits em português.
