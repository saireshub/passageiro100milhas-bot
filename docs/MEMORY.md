# 🧠 MEMORY - Contexto Persistente, Decisões e Lições Aprendidas

---

## 1. Estado Mental e Foco Atual do Projeto

- **Foco Primário:** Estruturar um bot leve, estável e autônomo que permita ao operador do canal Passageiro 100 Milhas criar e postar artes no Instagram pelo celular em menos de 1 minuto.
- **Premissa Operacional:** Zero custo operacional inicial aproveitando os benefícios acadêmicos do Azure for Students e uso de tecnologias limpas e fáceis de manter.

---

## 2. Decisões Arquiteturais e Lições Aprendidas

### 2.1 Geração de Imagem: HTML/CSS + Chromium CLI vs. Python PIL
- **Desafio:** Gerar artes de alta qualidade para o Instagram (1080x1350 px, proporção 4:5) com sombras, tipografia moderna, alinhamentos complexos e flexbox dinâmico.
- **Aprendizado:** A biblioteca Python Pillow (PIL) exige cálculo manual rigoroso de coordenadas $(x, y)$, quebra manual de linhas de texto e gera layouts rígidos. A abordagem com **Templates HTML/CSS** (compilados com Jinja2) oferece flexibilidade total de design, permite iteração rápida no visual sem mexer no código Python e manutenção visual trivial.

### 2.2 Compatibilidade e Execução do Renderizador (Chromium CLI vs. Playwright C-Bindings)
- **Desafio:** Em ambientes Windows corporativos ou protegidos por políticas de segurança rigorosas (AppControl/WDAC), bibliotecas como `greenlet` (usada pelo wrapper Python padrão do Playwright) podem ter o carregamento de DLLs `.pyd` bloqueado pelo sistema operacional.
- **Solução:** Implementamos a captura nativa via **Chromium CLI (`chrome-headless-shell` / Edge / Chrome)** através de chamadas assíncronas de subprocesso (`asyncio.create_subprocess_exec`). Isso garante 100% de compatibilidade multiplataforma sem depender de extensões compiladas em C em Python.

### 2.3 Meta Graph API (Publicação Oficial no Instagram & Facebook)
- **Desafio:** Evitar o risco de bloqueios, penalidades ou *shadowban* e garantir publicação direta e transparente no feed.
- **Aprendizado:** O uso da **Meta Graph API oficial** exige uma conta do Instagram do tipo Profissional/Criador vinculada a uma Página do Facebook e escopo `instagram_content_publish`.
- **Fluxo Obrigatório:** A API exige o upload da imagem em uma URL pública acessível, a criação de um *Media Container* (`POST /{ig-user-id}/media`) e a posterior chamada de publicação (`POST /{ig-user-id}/media_publish`).

### 2.4 Experiência de Uso (Telegram CMS & Human-in-the-Loop)
- **Desafio:** Evitar publicações acidentais, dados incorretos ou erros tipográficos em redes sociais públicas.
- **Aprendizado:** Adicionar uma etapa obrigatoriamente intermediária no Telegram, onde o bot renderiza a arte final e exibe uma prévia com botões inline (`[🚀 Confirmar e Publicar]`, `[✏️ Editar]` e `[❌ Cancelar]`), garante total controle operacional antes de enviar para as redes sociais.

### 2.5 Escolha de Nuvem e Dimensionamento (Render vs. Azure vs. Coolify)
- **Render Free:** O limite de 750 horas mensais compartilhadas impede rodar 2 serviços ao mesmo tempo e hiberna aplicações sem tráfego HTTP após 15 minutos, inviabilizando bots em modo *polling*.
- **Oracle Cloud:** Processo de cadastro possui barreiras rígidas de validação de cartão e detecção antifraude que impediram a criação da conta.
- **Coolify em VM pequena:** Exige no mínimo 2 GB a 4 GB de RAM para não sofrer OOM (*Out of Memory*). Em máquinas de 1 GB de RAM (como a B1s gratuita do Azure), é muito mais leve e estável gerenciar containers diretamente via **Docker Compose**.
- **Azure for Students:** Mostrou-se a melhor alternativa por conceder US$ 100 sem necessidade de cartão de crédito e 750h/mês de VM Linux B1s perene, mantendo o bot ativo 24/7 sem custos durante todo o período acadêmico.

---

## 3. Resumo de Problemas Conhecidos e Soluções (Gotchas)

| Sintoma / Erro | Causa Raiz | Solução Padronizada |
| :--- | :--- | :--- |
| `WinError 1260` ou DLL blocked no Playwright | WDAC / AppControl do Windows bloqueia DLLs | Usar execução direta do executável Chromium via `subprocess` assíncrono. |
| Erro Meta `2207001` (Media container not ready) | Tentativa de publicar antes de o Instagram baixar e processar a foto | Adicionar polling com delay de 2 a 5 segundos checando o `status_code` do container antes do `media_publish`. |
| Imagem cortada no feed do Instagram | Imagem gerada fora da proporção 4:5 ou com dimensões inadequadas | Fixar viewport exato de `1080x1350px` e aplicar safe zone de 60px. |
