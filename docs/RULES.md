# 📜 RULES - Regras de Código e Conduta Técnica

---

## 1. Padrões de Código e Guia de Estilo (Python)

### 1.1 Convenções de Nomenclatura
- **Arquivos e Módulos:** `snake_case` (ex: `telegram_bot.py`, `ocr_extractor.py`).
- **Funções e Variáveis:** `snake_case` (ex: `render_post_image()`, `creation_id`).
- **Classes e Modelos:** `PascalCase` (ex: `PostTrechoData`, `MetaApiClient`).
- **Constantes e Configurações:** `UPPER_SNAKE_CASE` (ex: `TELEGRAM_BOT_TOKEN`, `DEFAULT_VIEWPORT`).

### 1.2 Tipagem e Qualidade
- **Type Hints:** Obrigatório utilizar tipagem estática nas assinaturas de funções e retornos:
  ```python
  async def render_post_image(data: PostTrechoData) -> str:
      ...
  ```
- **Validação de Schemas:** Utilizar modelos Pydantic para validação de dados recebidos e estruturas de entrada.
- **Assincronismo:** Todas as operações de rede (chamadas Telegram, Meta API, Gemini/OCR) e renderização devem ser assíncronas com `async/await` e `asyncio`.

---

## 2. Tratamento de Exceções e Padrões de Logging

### 2.1 Padrão de Logging
- Utilizar o módulo nativo `logging` configurado com formato legível e timestamps:
  ```python
  import logging
  logger = logging.getLogger(__name__)
  ```
- Níveis de severidade:
  - `DEBUG`: Detalhes de renderização interna e payloads.
  - `INFO`: Comandos recebidos, posts gerados, aprovações e publicações bem-sucedidas.
  - `WARNING`: Tentativa de acesso de usuário não autorizado ou parâmetros fora do padrão.
  - `ERROR`: Falha na Meta API, erro de renderização ou queda de conexão.

### 2.2 Tratamento de Erros
- **Proibição de Captura Silenciosa:** Nunca utilizar blocos `except: pass` vazios.
- Sempre registrar o erro completo com `logger.exception("Mensagem de contexto")`.
- **Feedback ao Administrador:** Caso uma etapa falhe durante o fluxo no Telegram, responder ao usuário com uma mensagem clara sobre o ocorrido (ex: *"❌ Ocorreu uma falha ao renderizar a prévia da imagem. Tente novamente."*).

---

## 3. Gestão de Módulos e Dependências

- Todas as bibliotecas de terceiros devem ser registradas com versões estáveis no `requirements.txt`.
- Evitar pacotes pesados desnecessários ou que exijam compilações em C/C++ complexas no Windows se houver alternativa pura em Python ou chamada via CLI.
- Manter o código modular e desacoplado na pasta `services/`, evitando funções gigantes monolíticas em `main.py`.

---

## 4. Diretrizes de Conduta da IA

1. **Código Completo e Funcional:** Evitar snippets truncados com marcadores como `// resto do código aqui`. Entregar arquivos prontos para execução.
2. **Preservação de Contexto:** Não remover docstrings, comentários explicativos ou configurações existentes sem alinhamento prévio.
3. **Respeito à Arquitetura:** Não criar novos diretórios fora do padrão estabelecido em `ARCHITECTURE.md`.
4. **Commits Padronizados:** Seguir rigorosamente a regra de Conventional Commits em português estabelecida em `.agents/rules/commit_convention.md`.
