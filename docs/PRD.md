# 📄 PRD - Product Requirements Document
## Projeto: Passageiro 100 Milhas Bot

---

## 1. Visão Geral e Problema de Negócio

### 1.1 Contexto
O canal **Passageiro 100 Milhas** monitora e compartilha oportunidades de emissões de passagens aéreas com milhas e promoções de transferência/acúmulo de pontos. A agilidade na publicação é crítica, pois passagens baratas e vagas promocionais esgotam rapidamente.

### 1.2 O Problema
O fluxo tradicional de produção de conteúdo é moroso e burocrático:
1. Localizar a oportunidade no programa de milhas.
2. Abrir editor de imagens (Canva, Photoshop ou Figma) para montar a arte.
3. Ajustar tipografia, rota, valores, datas e alinhar elementos.
4. Exportar a imagem, redigir a legenda e abrir o app ou Meta Business Suite para publicar.

Esse processo consome tempo precioso, gerando gargalo operacional e risco de a oportunidade expirar antes da postagem.

### 1.3 A Solução
O **Passageiro 100 Milhas Bot** é um sistema headless com conceito **CMS via Telegram com Human-in-the-Loop**:
- O Telegram serve como a interface administrativa completa.
- O administrador envia dados por comando/formulário ou apenas encaminha um print de tela da oferta.
- O motor interno extrai os dados, gera uma imagem com design profissional em alta resolução (1080x1350px - 4:5) via HTML/CSS + headless Chromium e formata a legenda editorial padrão.
- O bot devolve a prévia completa no Telegram com botões de aprovação instantânea.
- Com um toque em **Confirmar e Publicar**, a publicação vai direto ao feed do Instagram via Meta Graph API oficial.

---

## 2. Linhas Editoriais e Tipos de Conteúdo

### 2.1 Tipo A: Alerta de Trecho (Emissão com Milhas)
- **Foco:** Imediatismo da oportunidade de voo.
- **Campos Mandatórios:**
  - Origem e Destino (Códigos IATA, ex: `GRU`, `MIA`).
  - Classe de cabine (Econômica, Premium Economy, Executiva).
  - Companhia Operadora e Programa de Fidelidade emissor.
  - Custo por trecho em milhas e valor das taxas de embarque.
  - Janela de datas encontradas (Ida / Volta).
  - Imagem de fundo opcional (cabine ou destino) ou uso de background padrão.

### 2.2 Tipo B: Informativo de Promoção (Transferência / Bônus / Compra)
- **Foco:** Análise de estratégia de pontos, comparativo de regras e veredito.
- **Campos Mandatórios:**
  - Parceria (ex: `Livelo ➔ LATAM Pass`).
  - Percentual de bônus máximo.
  - Data de validade da campanha.
  - Regras essenciais (clientes assinantes do clube vs clientes gerais, lote mínimo).
  - Veredito visual/análise rápida do custo do milheiro.

---

## 3. Funcionalidades Principais (Core Features)

1. **Entrada de Dados via Telegram:**
   - **Formulário Guiado:** Comandos `/trecho` e `/promo` que iniciam conversação passo a passo solicitando as variáveis da publicação.
   - **Extração Inteligente (OCR / Visão Computacional):** Envio direto de screenshots de emissões/telas de programas com preenchimento automático das informações via IA.
2. **Motor de Renderização Automatizado:**
   - Montagem de arte gráfica em alta fidelidade a partir de templates HTML/CSS compilados com Jinja2.
   - Renderização sem perdas em resolução `1080x1350` (formato vertical 4:5 nativo para o feed do Instagram).
3. **Mecanismo de Aprovação Humana (Human-in-the-Loop):**
   - Envio da imagem gerada e da legenda formatada na mesma conversa do Telegram.
   - Teclado interativo inline com opções de `[🚀 Confirmar e Publicar]`, `[✏️ Editar Dados]` e `[❌ Cancelar]`.
4. **Publicação Oficial na Meta Graph API:**
   - Upload de mídia e criação do container (`POST /{ig-user-id}/media`).
   - Verificação de status e disparo de publicação no feed (`POST /{ig-user-id}/media_publish`).
   - Retorno do link direto (permalink) do post publicado no chat do Telegram.

---

## 4. Histórias de Usuário (User Stories)

- **Como Administrador:** Quero cadastrar um trecho promocional em menos de 30 segundos pelo celular via Telegram para que meus seguidores recebam a dica antes que os assentos esgotem.
- **Como Administrador:** Quero enviar um print da tela do programa Smiles/LATAM Pass e ter os dados extraídos automaticamente para não precisar digitar todos os valores e taxas.
- **Como Administrador:** Quero visualizar a arte gráfica final e a legenda antes de ir ao ar para evitar erros de digitação e garantir controle editorial total.
- **Como Administrador:** Quero que a publicação no Instagram seja feita oficialmente pela API para não correr riscos de bloqueios ou penalidades de shadowban.

---

## 5. Critérios de Aceitação

- O bot deve responder exclusivamente ao `TELEGRAM_USER_ID` autorizado no `.env`.
- As imagens geradas devem ter proporção estrita 4:5 (`1080x1350px`) com tipografia nítida e contraste adequado.
- Nenhuma publicação pode ser disparada nas redes sociais sem a aprovação explícita do administrador no botão inline.
- Em caso de falha de conexão ou erro na Meta API, o bot deve notificar o administrador detalhando o motivo sem travar a aplicação.

---

## 6. Limites de Escopo (Out of Scope no MVP)

- **Não incluso no MVP:**
  - Painel administrativo web (a interface é 100% via Telegram).
  - Suporte a múltiplos administradores concorrentes com RBAC.
  - Carrossel de múltiplas imagens ou Stories no Instagram (foco em post único no feed).
  - Agendamento de posts em fila de data/hora futura (posts aprovados são publicados imediatamente).
  - Scraping automatizado de sites de companhias aéreas sem intervenção humana.
