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
| `META_ACCESS_TOKEN` | Token permanente de publicação no Instagram | Crítico |
| `INSTAGRAM_ACCOUNT_ID` | Identificador da conta profissional da Meta | Médio |
| `GEMINI_API_KEY` | Chave de acesso à API de IA/OCR | Alto |

---

## 3. Sanitização de Entradas e Proteção de Templates

### 3.1 Prevenção de Injeção em Templates HTML (XSS / Layout Breaking)
- Os dados digitados no Telegram (origem, destino, companhia, etc.) são renderizados em HTML pelo Jinja2.
- O Jinja2 deve operar com `autoescape=True` ativado para evitar injeção acidental de tags HTML ou scripts maliciosos.
- Dados de rota e texto passam por sanitização (remoção de caracteres de escape e validação de tamanho máximo) para impedir distorções visuais ou quebras no layout gerado pelo Chromium.

### 3.2 Validação de Mídias Recebidas
- Imagens enviadas para OCR ou usadas como fundo devem ter formato e tamanho validados antes de serem manipuladas pelo sistema de arquivos, evitando ataques de exaustão de disco (*Zip Bombs* / arquivos de tamanho excessivo).

---

## 4. Segurança de Infraestrutura e Redes

### 4.1 Máquina Virtual Azure
- **Grupo de Segurança de Rede (NSG):** Apenas as portas estritamente necessárias devem estar abertas:
  - Porta 22 (SSH) com acesso restrito preferencialmente via chave pública SSH.
  - Portas internas de contêineres não devem ser expostas publicamente sem proxy reverso seguro.
- **Isolamento de Contêiner:** O processo do bot roda dentro do contêiner Docker sem permissões de `root` sempre que possível.

### 4.2 Políticas e Boas Práticas com a Meta Graph API
- **Respeito a Rate Limits:** A API da Meta possui cotas de publicação por hora/dia. O bot implementa validações para não disparar requisições em loops rápidos acidentais.
- **Validação de Container State:** Sempre checar o status de preparação do container (`status_code == 'FINISHED'`) antes de chamar `media_publish` para evitar erros `2207001` (Media container not ready).
