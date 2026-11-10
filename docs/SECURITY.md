# 🔒 SECURITY - Diretrizes de Segurança e Proteção

---

## 1. Autenticação e Controle de Acesso (Telegram Whitelist)

O bot opera como um painel administrativo com permissão de publicação pública em redes sociais. Por essa razão, o acesso é estritamente restrito:

### 1.1 Verificação de Usuário Autorizado
- Todas as interações (comandos `/trecho`, `/promo`, envio de fotos e cliques em botões inline) devem passar por uma camada de validação do ID do remetente (`update.effective_user.id`).
- Se o ID do usuário não constar na variável de ambiente `TELEGRAM_USER_ID` (ou na lista de IDs autorizados em `config.py`), a requisição deve ser sumariamente ignorada ou descartada com log de aviso.
- **Regra:** Nunca permitir comandos abertos sem filtro de remetente.

```python
def is_authorized(user_id: int) -> bool:
    return str(user_id) == str(settings.TELEGRAM_USER_ID)
```

---

## 2. Gerenciamento de Segredos e Variáveis de Ambiente

### 2.1 Política de Chaves e Tokens
- **Proibição Absoluta de Hardcoding:** É estritamente proibido inserir tokens, chaves de API, senhas ou IDs confidenciais diretamente no código-fonte.
- **Arquivo `.env`:** O arquivo `.env` deve constar obrigatoriamente no `.gitignore` e nunca ser enviado para o repositório Git.
- **Arquivo `.env.example`:** Mantido versionado contendo apenas as chaves com valores fictícios/exemplo para guiar novos deploys.

### 2.2 Inventário de Segredos
| Variável | Finalidade | Nível de Sensibilidade |
| :--- | :--- | :--- |
| `TELEGRAM_BOT_TOKEN` | Token de controle total do bot Telegram | Crítico |
| `TELEGRAM_USER_ID` | Identificador do administrador autorizado | Alto |
| `META_ACCESS_TOKEN` | Token permanente de publicação na Meta (Instagram & Facebook) | Crítico |
| `INSTAGRAM_ACCOUNT_ID` | Identificador da conta profissional do Instagram | Médio |
| `FB_PAGE_ID` | Identificador da Página do Facebook vinculada | Médio |
| `GEMINI_API_KEY` | Chave de acesso à API do Google Gemini (Vision & Text) | Alto |
| `AZURE_STORAGE_CONNECTION_STRING` | String de conexão com o Azure Blob Storage | Crítico |

---

## 3. Sanitização de Entradas e Proteção de Templates

### 3.1 Prevenção de Injeção em Templates HTML (XSS / Layout Breaking)
- Os dados digitados no Telegram (origem, destino, companhia, etc.) são renderizados em HTML pelo Jinja2.
- O Jinja2 deve operar com `autoescape=True` ativado para evitar injeção acidental de tags HTML ou scripts maliciosos.
- Dados de rota e texto passam por sanitização (remoção de caracteres de escape e validação de tamanho máximo) para impedir distorções visuais ou quebras no layout gerado pelo Chromium.

### 3.2 Validação de Mídias Recebidas
- Imagens enviadas para OCR ou usadas como fundo devem ter formato e tamanho validados antes de serem manipuladas pelo sistema de arquivos, evitando ataques de exaustão de disco (*Zip Bombs* / arquivos de tamanho excessivo).

---

## 4. Segurança de Infraestrutura, CI/CD e Contêineres

### 4.1 Azure Container Apps & Isolamento
- **Ingress Desabilitado (Zero Superfície HTTP Exposta):** O aplicativo `app-passageiro100milhas` opera em modo *polling* privado com o Telegram, não expondo nenhuma porta HTTP/SSH pública na internet.
- **Execução Não-Root:** O contêiner Docker roda estritamente sob o usuário `appuser` (UID `1001`) com ambiente de perfil isolado em `/home/appuser` e `/tmp/chromium-data`.
- **Links Efêmeros (SAS Token 24h):** O container do Azure Blob Storage permanece privado. As imagens publicadas recebem apenas URLs temporárias assinadas com permissão exclusiva de leitura válidas por 24 horas para download da Meta API.

### 4.2 Autenticação Sem Senhas no CI/CD (OIDC Federation)
- O deploy contínuo no GitHub Actions (`.github/workflows/deploy.yml`) não armazena credenciais estáticas de administração da Azure (`clientSecret`).
- O workflow utiliza **OpenID Connect (OIDC)** assumindo a Identidade Gerenciada `id-github-passageiro100milhas` via token JWT de curta duração, com permissão restrita exclusivamente ao escopo do grupo de recursos `rg-passageiro100milhas-mx`.

### 4.3 Políticas e Boas Práticas com a Meta Graph API
- **Respeito a Rate Limits:** A API da Meta possui cotas de publicação por hora/dia. O bot implementa validações para não disparar requisições em loops rápidos acidentais.
- **Validação de Container State:** Sempre checar o status de preparação do container (`status_code == 'FINISHED'`) antes de chamar `media_publish` no Instagram para evitar erros `2207001` (Media container not ready).
