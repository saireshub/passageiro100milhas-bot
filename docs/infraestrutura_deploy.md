# Planejamento de Infraestrutura e Deploy

Este documento registra a análise de opções de hospedagem, decisões de arquitetura de nuvem e os parâmetros para a continuidade do deploy no **Azure for Students**.

---

## 1. Histórico de Análise de Provedores

### 1.1 Render (Plano Free)
* **Limitação:** Oferece apenas **750 horas gratuitas compartilhadas por mês** por conta.
* **Impacto:** Rodar duas aplicações em paralelo esgota o limite no meio do mês (~dia 15). Além disso, serviços sem requisições HTTP de entrada entram em hibernação após 15 minutos, o que afeta bots em modo *polling*.

### 1.2 Oracle Cloud (Always Free)
* **Status:** Cadastro não concluído devido a restrições/validações rígidas no formulário de verificação da Oracle.
* **Decisão:** Descartado para o momento para focar no ecossistema Azure.

### 1.3 Microsoft Azure for Students (Provedor Selecionado)
* **Vantagens:**
  * **US$ 100 de créditos anuais** sem necessidade de cartão de crédito.
  * **VM B1s gratuita (750 horas/mês):** Permite manter 1 servidor ligado 24/7 durante 12 meses.
  * Suporte nativo a Docker e imagens customizadas Linux (Ubuntu).

---

## 2. Estratégias de Deploy na VM Azure (1 Instância vs. Coolify)

Avaliou-se a possibilidade de usar o **Coolify** (PaaS self-hosted com painel web) versus **Docker Compose direto**:

| Critério | Estratégia A: Docker Compose Direto (Recomendada) | Estratégia B: Coolify no Azure |
| :--- | :--- | :--- |
| **Tamanho da VM** | `Standard_B1s` (1 vCPU, 1 GB RAM + 2 GB Swap) | `Standard_B2s` (2 vCPUs, 4 GB RAM) |
| **Custo Mensal** | **R$ 0,00** (coberto pelas 750h gratuitas perenes) | ~US$ 25 a US$ 30 / mês (consome os créditos) |
| **Duração do Benefício**| **12 meses ininterruptos** com US$ 100 de créditos preservados | **~3 a 4 meses** até consumir os US$ 100 |
| **Gerenciamento** | Terminal SSH + `docker compose` | Interface web gráfica amigável |
| **Consumo do Bot** | O bot com Chromium roda leve e estável | Coolify + Postgres + Bot competem por RAM |

> **Decisão Operacional:** Recomenda-se iniciar com a **Estratégia A (VM B1s)** para garantir 1 ano de hospedagem 100% gratuita. Caso no futuro prefira a facilidade visual do Coolify, basta redimensionar a VM para `B2s` no portal do Azure em poucos cliques.

---

## 3. Roteiro de Retomada para Amanhã

### Passo 1: Ativação da Conta Azure for Students
* Acessar: [https://azure.microsoft.com/free/students/](https://azure.microsoft.com/free/students/)
* Fazer login com o **e-mail universitário/acadêmico**.
* Validar com número de celular via SMS (não pede cartão).

### Passo 2: Criação da Máquina Virtual (VM)
No portal do Azure, ir em **"Máquinas Virtuais"** > **"Criar"**:
* **Assinatura:** `Azure for Students`
* **Grupo de Recursos:** `rg-passageiro100milhas`
* **Nome:** `vm-passageiro100milhas`
* **Região:** `East US`
* **Imagem:** `Ubuntu 24.04 LTS` (Gen2)
* **Tamanho:** `Standard_B1s` (1 vCPU, 1 GiB RAM)
* **Autenticação:** Chave SSH ou Senha
* **Portas de Entrada:** SSH (porta 22)

### Passo 3: Deploy do Bot na VM (Comandos Prontos)
Após conectar via SSH (`ssh seu_usuario@ip_da_vm`):
```bash
# 1. Instalar Docker e Git (caso não venham instalados)
sudo apt update && sudo apt install -y docker.io docker-compose-v2 git

# 2. Clonar o repositório
git clone https://github.com/saireshub/passageiro100milhas-bot.git
cd passageiro100milhas-bot

# 3. Configurar variáveis de ambiente
nano .env   # Colar as chaves do Telegram, Gemini e Meta

# 4. Iniciar o bot em segundo plano
sudo docker compose up -d --build

# 5. Monitorar logs
sudo docker compose logs -f
```
