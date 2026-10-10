# Lições Aprendidas e Decisões de Projeto

Este documento registra os aprendizados técnicos, escolhas de arquitetura e soluções para desafios encontrados no desenvolvimento do bot **Passageiro 100 Milhas**.

---

## 1. Geração de Imagem: HTML/CSS + Chromium CLI vs. Python PIL
* **Desafio:** Gerar artes de alta qualidade para o Instagram (1080x1350 px, proporção 4:5) com sombras, tipografia moderna e flexbox dinâmico.
* **Aprendizado:** A biblioteca Python Pillow (PIL) exige cálculo manual rigoroso de coordenadas $(x, y)$ e quebra manual de texto. A abordagem com **Templates HTML/CSS** (compilados com Jinja2) oferece flexibilidade total de design de forma muito simples e fácil manutenção visual.

---

## 2. Compatibilidade e Execução do Renderizador (Chromium CLI)
* **Desafio:** Em ambientes Windows corporativos/protegidos por politicas de segurança (AppControl/WDAC), bibliotecas como `greenlet` (usada pelo wrapper Python do Playwright) podem ter o carregamento de DLLs `.pyd` bloqueado.
* **Solução:** Implementamos a captura nativa via **Chromium CLI (`chrome-headless-shell` / Edge / Chrome)** através de chamadas assíncronas do sistema (`asyncio.create_subprocess_exec`). Isso garante 100% de compatibilidade sem depender de extensões C compiladas em Python.

---

## 3. Meta Graph API (Instagram & Facebook Publishing)
* **Desafio:** Evitar o risco de bloqueios ou *shadowban* e garantir publicação direta no feed.
* **Aprendizado:** O uso da **Meta Graph API oficial** exige uma conta do Instagram do tipo Profissional/Criador vinculada a uma Página do Facebook e escopo `instagram_content_publish`.
* **Fluxo Obrigatório:** A API exige o upload da imagem em um URL público acessível, a criação de um *Media Container* (`POST /{ig-user-id}/media`) e a posterior chamada de publicação (`POST /{ig-user-id}/media_publish`).

---

## 4. Experiência de Uso (Telegram CMS & Human-in-the-Loop)
* **Desafio:** Evitar publicações acidentais ou com erros de digitação.
* **Aprendizado:** Adicionar uma etapa obrigatoriamente intermediária no Telegram, onde o bot renderiza a arte final e exibe uma prévia com botões inline (`[🚀 Confirmar e Publicar]` e `[❌ Cancelar]`), garante total controle operacional antes de enviar para as redes sociais.

---

## 5. Escolha de Nuvem e Dimensionamento (Render vs. Azure vs. Coolify)
* **Render Free:** O limite de 750 horas mensais compartilhadas impede rodar 2 serviços ao mesmo tempo e hiberna aplicações sem tráfego HTTP após 15 minutos.
* **Oracle Cloud:** Processo de cadastro possui barreiras rígidas de validação de cartão e fraud prevention que dificultam a criação da conta.
* **Coolify em VM pequena:** Exige no mínimo 2 GB a 4 GB de RAM para não sofrer OOM (Out of Memory). Em máquinas de 1 GB de RAM (como a B1s gratuita do Azure), é muito mais leve e estável gerenciar múltiplos containers diretamente via **Docker Compose**.
* **Azure for Students:** Mostrou-se a opção mais viável por conceder US$ 100 sem cartão e 750h/mês de VM Linux B1s gratuita, permitindo manter o bot 24/7 durante 1 ano.
