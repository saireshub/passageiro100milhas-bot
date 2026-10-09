on# Planejamento do Projeto: Passageiro 100 Milhas (MVP)

## 1. Arquitetura e Fluxo Operacional do MVP

O fluxo foi desenhado para remover o atrito de criação diária de posts, utilizando o Telegram como o "painel de controle" (CMS) do administrador.

```text
[Você via Telegram] 
       │ (Envia comando ou formulário rápido)
       ▼
[Bot Telegram (Webhook em Python)]
       │
       ├─► 1. Extrai variáveis (Origem, Destino, Milhas, Taxas, Datas / Regras da Promoção)
       ├─► 2. Renderiza imagem baseada em template HTML/CSS
       ├─► 3. Salva mídia temporária (Cloudflare R2 / S3 ou storage local)
       ▼
[Meta Graph API (Instagram & Facebook)]
       │
       └─► Publica Carrossel/Imagem Única + Legenda formatada
```

---

## 2. Estrutura dos Posts e Templates

O projeto prevê duas linhas editoriais principais. Cada uma exige tratamentos de imagem e legendas distintos.

### Tipo A: Alerta de Trecho (Emissão com Milhas)
Focado no imediatismo da oportunidade. Exige clareza visual instantânea sobre a rota e o custo.

* **Elementos da Imagem (1080x1350 px - 4:5):**
  * **Cabeçalho:** Rota em destaque com códigos IATA (ex: `GIG ✈ CDG`).
  * **Fundo:** Foto da cabine ou destino com overlay escuro (40-50% de opacidade) para garantir legibilidade.
  * **Destaque:** Custo em milhas em fonte pesada e valor das taxas logo abaixo.
  * **Rodapé:** Logo do programa, companhia aérea e janela de datas.

* **Template da Legenda:**
```text
🚨 ALERTA DE EMISSÃO: [ORIGEM (IATA)] ✈️ [DESTINO (IATA)]

Classe: [Econômica / Premium Economy / Executiva]
Companhia Operadora: [Nome da Cia Aérea]
Programa: [Nome do Programa]

💰 CUSTO POR TRECHO:
• Milhas: [Valor] milhas
• Taxas: R$ [Valor]

📅 DATAS ENCONTRADAS:
Ida: [Datas]
Volta: [Datas]

⚠️ Dica rápida: Disponibilidade sujeita à alteração rápida pelos programas. Encontrou? Emita imediatamente.
```

### Tipo B: Informativo de Promoção (Transferência/Compra)
Focado em estratégia, com visual mais limpo, analítico e comparativo.

* **Elementos da Imagem (1080x1350 px - 4:5):**
  * **Design:** Minimalista, estilo card ou editorial com alto contraste.
  * **Gancho:** Título com o benefício máximo (ex: `ATÉ 100% DE BÔNUS: LIVELO ➔ LATAM PASS`).
  * **Corpo:** Tabela rápida ou bullets comparando condições (ex: Clube vs. Standard).
  * **Selo:** Veredito visual (Excelente, Regular, Ruim).

* **Template da Legenda:**
```text
🔥 PROMOÇÃO: [Origem] ➔ [Destino]

Bônus máximo: até [X]%
Validade: até [Data]

📌 REGRAS BÁSICAS:
• [X]% para assinantes do Clube [Nome]
• [Y]% para demais clientes
• Transferência mínima: [Z] pontos

💡 ANÁLISE DO PASSAGEIRO:
[Breve análise do custo do milheiro e se compensa o risco de transferência]

🔗 Link oficial e regulamento no story ou link da bio.
```

---

## 3. Métodos de Geração de Imagem

Para transformar os dados do Telegram em imagens padronizadas para o Instagram, avaliamos três abordagens:

| Método | Como Funciona | Prós | Contras |
| :--- | :--- | :--- | :--- |
| **HTML/CSS + Playwright** (Recomendado) | Usa um template web (HTML/CSS) e tira um screenshot via Chromium headless. | Layout responsivo perfeito, sombras, flexbox e facilidade de manutenção. | Maior consumo de memória RAM do servidor para rodar o headless browser. |
| **Python Pillow (PIL)** | Desenha texto e formas diretamente sobre uma imagem base via coordenadas exatas (x,y). | Ultraleve, rápido, roda em qualquer VPS barata. | Manutenção trabalhosa caso mude o tamanho do texto ou layout. |
| **Satori (Vercel/OG)** | Converte markup JSX/HTML para SVG/PNG. | Leve e sem navegador. | Limitação de propriedades CSS suportadas e exige Node.js. |

---

## 4. Stack de Ferramentas Selecionadas

| Componente | Ferramenta/Tecnologia | Justificativa para o MVP |
| :--- | :--- | :--- |
| **Entrada de Dados** | Telegram Bot API (`python-telegram-bot`) | Interface pronta mobile/desktop, botões interativos e zero custo. |
| **Backend** | Python (FastAPI) | Ágil, robusto e ecossistema farto de integrações. |
| **Renderização** | Playwright (Screenshot de HTML) | Permite construir layouts incríveis apenas sabendo HTML/CSS. |
| **Publicação** | Meta Graph API (Instagram/Facebook) | Publicação oficial direto no feed sem risco de shadowban. |
| **Hospedagem** | Render / Railway / Fly.io | Setup fácil via Docker para rodar o app Python + Playwright. |

---

## 5. Roteiro de Execução (Roadmap)

### Fase 1: Setup de Contas
- [ ] Mudar conta do Instagram para Profissional/Criador.
- [ ] Criar página vinculada no Facebook.
- [ ] Registrar app no Meta for Developers, aprovar escopo `instagram_content_publish` e gerar token de acesso de longa duração.
- [ ] Criar bot no Telegram via `@BotFather` e guardar o token.

### Fase 2: Templates Visuais
- [ ] Criar `trecho_template.html` (com CSS para acomodar título, rota, milhas e foto de fundo).
- [ ] Criar `promo_template.html` (design limpo de cards de texto).

### Fase 3: Desenvolvimento do Backend (Python)
- [ ] Desenvolver fluxo conversacional do bot (Ex: Comando `/trecho`, aguardar dados, preencher dicionário).
- [ ] Integrar script de captura de tela com Playwright gerando o `post.png`.
- [ ] Integrar Meta Graph API para receber a imagem e o texto e publicar via requisição POST.

### Fase 4: Validação (O fluxo "Aprovar")
- [ ] Bot gera a imagem, envia no chat para visualização com teclado inline: `[Publicar]` ou `[Cancelar]`.
- [ ] Ao clicar em "Publicar", o script finaliza a jornada na Meta API.