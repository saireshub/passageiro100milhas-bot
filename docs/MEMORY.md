# 🧠 MEMORY - Contexto Persistente, Decisões e Lições Aprendidas

---

## 1. Estado Mental e Foco Atual do Projeto

- **Foco Primário:** Estruturar um bot leve, estável e autônomo que permita ao operador do canal Passageiro 100 Milhas criar e postar artes simultaneamente no Instagram e Facebook pelo celular em menos de 1 minuto.
- **Premissa Operacional:** Zero custo operacional inicial aproveitando os benefícios do Azure for Students e uso de tecnologias limpas, serverless e fáceis de manter.

---

## 2. Decisões Arquiteturais e Lições Aprendidas

### 2.1 Geração de Imagem: HTML/CSS + Chromium CLI vs. Python PIL
- **Desafio:** Gerar artes de alta qualidade para o Instagram (1080x1350 px, proporção 4:5) com sombras, tipografia moderna e flexbox dinâmico.
- **Aprendizado:** A biblioteca Python Pillow (PIL) exige cálculo manual rigoroso de coordenadas $(x, y)$ e quebra manual de linhas. A abordagem com **Templates HTML/CSS** (compilados com Jinja2) oferece flexibilidade total de design, permite iteração rápida no visual sem mexer no código Python e manutenção visual trivial.

### 2.2 Compatibilidade e Execução do Renderizador (Chromium CLI)
- **Desafio:** Em ambientes protegidos por políticas de segurança rigorosas (AppControl/WDAC no Windows), wrappers padrão como `playwright-python` podem ter o carregamento de DLLs `.pyd` (como `greenlet`) bloqueado.
- **Solução:** Implementamos a captura nativa via **Chromium CLI (`chrome-headless-shell` / Edge / Chrome)** através de chamadas assíncronas de subprocesso (`asyncio.create_subprocess_exec`). Isso garante 100% de compatibilidade multiplataforma no Windows, Linux e Docker.

### 2.3 Meta Graph API e Armazenamento Temporário (Azure Blob com SAS)
- **Desafio:** A Meta Graph API exige uma URL HTTPS pública (`image_url`) para baixar a imagem ao criar o container. Um caminho local (`/app/output/...`) falha imediatamente.
- **Solução Adotada:** Upload para o **Azure Blob Storage** com geração de token **SAS (Shared Access Signature)** de leitura válido por 24 horas (`services/storage_service.py`). Isso permite manter o container de blobs estritamente privado na nuvem, garantindo segurança máxima e permitindo que apenas a Meta faça o download dentro do período de publicação.
- **Polling de Prontidão:** Adicionado polling ativo no `services/meta_api.py` verificando `status_code == 'FINISHED'` antes de chamar `/media_publish`, eliminando o erro `2207001` (Media container is not ready).

### 2.4 Segurança Operacional do Bot Telegram
- **Desafio:** Como o bot roda em modo polling, qualquer usuário que descobrisse o `@username` poderia disparar comandos ou publicar no feed público.
- **Solução:** Implementação do decorator `@admin_only` em `services/telegram_bot.py`. O bot valida se `update.effective_user.id == Config.TELEGRAM_USER_ID`. Qualquer usuário não autorizado tem a requisição sumariamente bloqueada com mensagem informativa exibindo o ID do remetente.

### 2.5 Infraestrutura na Nuvem: Azure Container Apps vs. VM Tradicional
- **Azure for Students (Políticas e Restrições):**
  1. *Restrição de Regiões:* Assinaturas de estudante possuem a política `Allowed resource deployment regions` limitando a criação a datacenters específicos (`mexicocentral`, `canadacentral`, `italynorth`, etc.).
  2. *Cota de VMs (vCPU = 0):* A Microsoft frequentemente zera a cota de VMs brutas para evitar abusos/mineração em contas acadêmicas.
  3. *ACR Tasks Desativado:* O comando `az acr build` é bloqueado na assinatura de estudantes (*TasksOperationsNotAllowed*).
- **Decisão Final:** Migração da arquitetura de VM para **Azure Container Apps (Serverless)** integrado com **Azure Container Registry (ACR)** e **GitHub Actions (CI/CD)**:
  - Elimina a necessidade de gerenciar sistema operacional, SSH e arquivos Swap.
  - A imagem Docker é compilada gratuitamente pelos runners do **GitHub Actions** e enviada para o ACR.
  - O contêiner roda 24/7 de forma estável e com reinício automático.

### 2.6 Deploy Contínuo Sem Senhas (OIDC com Identidade Gerenciada)
- **Desafio:** A conta acadêmica/usuário padrão não possui permissão de diretório no Microsoft Entra ID (`Application Administrator`) para criar Service Principals tradicionais via `az ad sp create-for-rbac` nem pelo assistente do Portal Azure.
- **Solução Moderna (Workload Identity Federation):** Criamos uma **User-Assigned Managed Identity** (`id-github-passageiro100milhas`) dentro do próprio grupo de recursos (`rg-passageiro100milhas-mx`) com role `Contributor` e credencial federada **OIDC** apontando exatamente para o `subject` emitido pelo GitHub Actions (`repo:saireshub@230404120/passageiro100milhas-bot@1412377456:ref:refs/heads/main`).
- **Resultado:** Zero segredos de senha expirando; a cada `git push`, o GitHub Actions autentica na Azure via token OIDC temporário, compila a imagem Python 3.12, publica as tags via `docker/metadata-action` e atualiza a revisão do Container App automaticamente.

---

## 3. Resumo de Problemas Conhecidos e Soluções (Gotchas)

| Sintoma / Erro | Causa Raiz | Solução Padronizada |
| :--- | :--- | :--- |
| `WinError 1260` no Playwright | WDAC / AppControl do Windows bloqueia DLLs | Usar execução direta do executável Chromium via `subprocess` assíncrono e remover `playwright` do `requirements.txt`. |
| Erro Meta `2207001` (Container not ready) | Tentativa de publicar antes de o Instagram baixar e processar a foto | Adicionar polling com checagem do `status_code == 'FINISHED'`. |
| `ExpressAzureMonitorLogDestNotSupported` no Container Apps | Região Mexico Central no modo Express rejeita logs corporativos | Criar o ambiente de contêineres com `--logs-destination none`. |
| `TasksOperationsNotAllowed` no ACR | Azure for Students bloqueia `az acr build` na nuvem | Utilizar **GitHub Actions** gratuito para compilar a imagem e fazer push ao ACR. |
| Erro OCR / Extração de imagem | `ocr_extractor` antigo hardcoded para DeepSeek inexistente | Migração para `services/gemini_service.py` com Google Gemini multimodal e remoção do arquivo legado. |
| Timeout / Falha JSON na imagem Gemini | Imagens pesadas (>5MB) de smartphones e respostas com markdown | Adicionada compressão Pillow (max 1536px), `responseMimeType: application/json` e parser regex flexível. |
| Chromium CLI `Failed to create headless user data directory` | Usuário não-root no Docker sem pasta HOME ou `--user-data-dir` | Adicionado `--user-data-dir` dinâmico em `/tmp`, `HOME=/home/appuser` e permissão no Dockerfile. |
| Meta API `Unsupported post request / Object ID does not exist` | Usou FB_PAGE_ID em vez de INSTAGRAM_ACCOUNT_ID no endpoint /media | Auto-resolução do Instagram Business Account ID (`17841467398304099`) via Graph API a partir do Page ID. |
| Crossposting Instagram & Facebook | O endpoint anterior só publicava no Instagram | Implementado envio simultâneo para Instagram Feed e Facebook Page (`/{page_id}/photos`). |
| Cache travado de `:latest` no Container Apps | Nós do Azure não re-baixam `:latest` se já existir no disco | Automação com `docker/metadata-action` gerando tags `:sha-xxxxxxx` únicas e imutáveis a cada commit. |
| Deploy pegava `:main` em vez de `:sha-` | `docker/metadata-action` ordena `type=ref` (prio 600) acima de `type=sha` (prio 100) | Definir `priority=999` em `type=sha` e filtrar com `grep ':sha-'` antes de chamar `az containerapp update`. |
| `Insufficient privileges` ao criar SP / Assistente Portal | Falta de permissão de registro de apps no diretório Entra ID | Uso de User-Assigned Managed Identity no grupo de recursos com federação OIDC para o GitHub Actions. |
| `AADSTS700213: No matching federated identity` | GitHub envia IDs numéricos no subject claim (`@230404120` e `@1412377456`) | Atualizar o `--subject` da credencial federada com o formato exato `repo:saireshub@230404120/passageiro100milhas-bot@1412377456:ref:refs/heads/main`. |
| Injeção acidental em templates / Acúmulo em disco | Falta de `autoescape=True` no Jinja2 e imagens temporárias persistentes | Ativar `autoescape=True` no `renderer.py` e remover `.png` temporária após envio/cancelamento em `telegram_bot.py`. |
| Fundos locais pesados / perda de rotação em redeploy | Fotos brutas (~7.5 MB), Chromium bloqueando `file:///` em `/tmp` e disco efêmero no Container Apps | Padronizar `bg_01.jpg`..`bg_07.jpg` em `1080x1350`px (~1.37 MB), passar `--allow-file-access-from-files` ao Chromium e persistir `state/bg_index.txt` no Azure Blob Storage. |
| `Timed out` ao enviar/publicar imagens no Telegram | Timeouts padrão de 5s no `python-telegram-bot` + chamadas HTTP/Blob síncronas travando o event loop `asyncio` | Aumentar timeouts no `Application.builder()` (`read=60s`, `media_write=120s`, `connect=20s`), mover chamadas síncronas para `asyncio.to_thread` e limitar Chromium com `asyncio.wait_for`. |
