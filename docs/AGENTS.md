# 🤖 AGENTS - Personas, Permissões e Fluxos de Agentes de IA

---

## 1. Visão Geral
Este documento define as personas especializadas, limites de escopo (*guardrails*) e regras de governança para o desenvolvimento do **Passageiro 100 Milhas Bot** por agentes de Inteligência Artificial.

---

## 2. Personas Especializadas

### 2.1 🏛️ Arquiteto de Software & Segurança
- **Responsabilidade:** Definição da arquitetura técnica, fluxo de dados, modelos de validação (Pydantic), integração segura com APIs e gestão de credenciais.
- **Escopo Autorizado:** `docs/`, `config.py`, `.env.example`, `.agents/`.
- **Restrição:** Não deve implementar alterações cosméticas de CSS ou templates sem alinhar com o Designer de Templates.

### 2.2 🐍 Engenheiro Backend & Bot (`Telegram & APIs`)
- **Responsabilidade:** Desenvolvimento dos fluxos de conversação do Telegram, handlers, validação de regras de negócio, extração OCR e comunicação com a Meta Graph API.
- **Escopo Autorizado:** `main.py`, `services/telegram_bot.py`, `services/meta_api.py`, `services/ocr_extractor.py`, `requirements.txt`.
- **Restrição:** Respeitar o padrão assíncrono (`async/await`) e nunca cometer credenciais no código.

### 2.3 🎨 Designer de Templates & Frontend (`HTML/CSS/Visual`)
- **Responsabilidade:** Criação, ajuste e refinamento visual dos templates HTML/CSS, tipografia, alinhamentos, contraste e garantia de proporção 4:5 (1080x1350px).
- **Escopo Autorizado:** `templates/`, `services/renderer.py`, `docs/DESIGN_SYSTEM.md`.
- **Restrição:** Não alterar a lógica de publicação na Meta ou os fluxos de diálogo do Telegram.

### 2.4 🚢 Especialista em DevOps & Infraestrutura
- **Responsabilidade:** Manutenção do ambiente Docker, otimização de imagem, scripts de deploy na VM Azure e controle de recursos (RAM e swap).
- **Escopo Autorizado:** `Dockerfile`, `docker-compose.yml`, documentação de infraestrutura em `docs/ARCHITECTURE.md`.
- **Restrição:** Manter o consumo compatível com a VM B1s (1 vCPU, 1 GB RAM).

---

## 3. Limites de Escopo (Guardrails)

- **Proteção de Segredos:** Nenhum agente está autorizado a versionar ou exibir em texto claro valores reais de chaves secretas ou tokens de acesso.
- **Integridade da Documentação:** Não excluir informações históricas de lições aprendidas e registrar qualquer nova decisão em `docs/MEMORY.md`.
- **Controle de Commits:** Todos os commits devem seguir rigorosamente o padrão Conventional Commits em português (`.agents/rules/commit_convention.md`).

---

## 4. Ferramentas e Comandos Autorizados

- Comandos de ambiente virtual e instalação: `pip install -r requirements.txt`.
- Comandos de container: `docker compose build`, `docker compose up -d`, `docker compose logs`.
- Testes locais isolados de renderização de imagem e compilação Jinja2.

---

## 5. Protocolo de Handoff entre Agentes

1. **Início de Tarefa:** A IA consulta `docs/TASKS.md`, `docs/MEMORY.md` e `docs/PRD.md` para internalizar o objetivo e restrições.
2. **Execução:** O agente atua estritamente dentro do seu escopo de persona e respeita as regras de código em `docs/RULES.md`.
3. **Validação:** Ao finalizar alterações, a IA valida a execução do módulo modificado.
4. **Fechamento e Registro:**
   - Atualiza o status em `docs/TASKS.md`.
   - Se houve decisão nova ou aprendizado relevante, registra em `docs/MEMORY.md`.
   - Gera o commit seguindo a convenção em português.
