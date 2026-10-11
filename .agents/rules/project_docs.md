# 🗺️ Regra de Documentação do Projeto (`docs/`)

## 📌 Objetivo
Este documento define a estrutura e o padrão oficial de documentação de projetos.
**Diretriz para Agentes e IA:** Sempre que for iniciar uma nova tarefa, estruturar uma nova funcionalidade ou tiver dúvidas sobre o escopo e regras, consulte a pasta `docs/`. Se algum arquivo estiver desatualizado ou ausente, sugira atualizações ou crie-o baseando-se no código atual e nas diretrizes abaixo.

---

## 📂 Estrutura de Arquivos Obrigatória (`docs/`)

Todos os projetos devem manter a estrutura padronizada composta pelos 9 arquivos abaixo:

### 1. `docs/PRD.md` (Product Requirements Document)
- **Função:** Coração funcional e de negócios do projeto.
- **Conteúdo Obrigatório:**
  - Visão geral e o problema que o software resolve.
  - Lista de funcionalidades principais (Core Features).
  - Histórias de usuários (User Stories) e fluxos de uso.
  - Critérios de aceitação e definição do que está fora de escopo (*out of scope*).
- **Como a IA deve usar:** Consultar para entender *o que* e *por que* estamos construindo, alinhando o código com os objetivos de negócio.

### 2. `docs/ARCHITECTURE.md` (Arquitetura e Infraestrutura)
- **Função:** Mapa técnico do sistema.
- **Conteúdo Obrigatório:**
  - Stack tecnológica completa (linguagens, bibliotecas, ferramentas).
  - Padrão arquitetural (ex: Modular, Clean Architecture, MVC).
  - Estrutura completa de diretórios e convenções de pastas.
  - Fluxo de dados entre frontend/interfaces, backend, serviços externos e integrações.
  - Infraestrutura, hospedagem e estratégias de deploy (Docker, Cloud, etc.).
- **Como a IA deve usar:** Seguir rigorosamente a arquitetura estabelecida sem inventar pastas ou dependências incompatíveis.

### 3. `docs/DATABASE.md` (Modelagem de Dados e Persistência)
- **Função:** Fonte da verdade sobre dados e esquemas de armazenamento.
- **Conteúdo Obrigatório:**
  - SGBD utilizado ou mecanismo de persistência/schemas em memória.
  - Convenções de nomenclatura e tipagem de dados.
  - Modelos, entidades, schemas (ex: Pydantic models) e relacionamentos.
  - Regras de migrations, seeds e armazenamento transitório de arquivos.
- **Como a IA deve usar:** Consultar antes de escrever queries, schemas ou criar novos models.

### 4. `docs/SECURITY.md` (Segurança e Proteção)
- **Função:** Diretrizes de proteção do sistema e dos dados.
- **Conteúdo Obrigatório:**
  - Autenticação e Autorização (políticas de acesso, verificação de ID do admin).
  - Gerenciamento de segredos (`.env`, proibição absoluta de hardcoding de tokens/keys).
  - Proteção de dados, sanitização de inputs e tratamento seguro de mídias.
  - Políticas de rede, rate limiting e boas práticas com APIs de terceiros.
- **Como a IA deve usar:** Garantir camadas de proteção e validação por padrão em todo código gerado.

### 5. `docs/RULES.md` (Regras de Código e Conduta)
- **Função:** Manual de estilo, linting e boas práticas técnicas.
- **Conteúdo Obrigatório:**
  - Padrões de nomenclatura e guia de estilo de código (PEP 8, type hints, etc.).
  - Tratamento de exceções, padrões de logging e retornos padronizados.
  - Restrições e diretrizes de IA (não utilizar bibliotecas depreciadas, manter comentários úteis).
- **Como a IA deve usar:** Aplicar como filtro de qualidade antes de gerar ou refatorar qualquer código.

### 6. `docs/DESIGN_SYSTEM.md` (Interface e Experiência)
- **Função:** Guia de padronização visual e comunicação.
- **Conteúdo Obrigatório:**
  - Especificações visuais de templates (resoluções, proporções, CSS, paleta de cores).
  - Tipografia, contraste, composição de elementos e cards visuais.
  - Padrões editoriais de texto, emojis e formatação de legendas/mensagens.
- **Como a IA deve usar:** Consultar ao criar ou refatorar templates, layouts e copies informativas.

### 7. `docs/TASKS.md` (Gestão de Progresso / Kanban)
- **Função:** Acompanhamento do ciclo de vida das tarefas.
- **Conteúdo Obrigatório:**
  - Seções: `To-Do` (A fazer), `In Progress` (Em andamento) e `Done` (Concluído).
  - Histórico de entregas e roadmap de evolução.
- **Como a IA deve usar:** Consultar para identificar o status do projeto e atualizar o status das tarefas após cada implementação.

### 8. `docs/MEMORY.md` (Contexto Persistente e Lições Aprendidas)
- **Função:** Cérebro contínuo do agente para evitar perda de contexto histórico.
- **Conteúdo Obrigatório:**
  - Lições aprendidas e desafios técnicos superados.
  - Decisões de arquitetura fundamentadas e trade-offs avaliados.
  - Soluções para bugs recorrentes e restrições de ambiente documentadas.
- **Como a IA deve usar:** Ler no início de toda sessão para recuperar o histórico e registrar novos aprendizados ao concluir tarefas complexas.

### 9. `docs/AGENTS.md` (Personas e Fluxos de Agentes de IA)
- **Função:** Definição de papéis, permissões e fluxos de trabalho para sistemas de agentes.
- **Conteúdo Obrigatório:**
  - Personas especializadas e responsabilidades.
  - Limites de escopo (*guardrails*) e regras de modificação de arquivos.
  - Ferramentas, comandos de terminal e skills permitidos.
  - Protocolos de handoff e validação entre personas.
- **Como a IA deve usar:** Adotar a persona adequada para a demanda atual e respeitar os limites de edição estabelecidos.
