# Arquitetura e Fluxo do Sistema

## 1. Visão Geral
O bot **Passageiro 100 Milhas** é um sistema headless que integra o Telegram como interface de gerenciamento (CMS), o Playwright para renderização de artes HTML/CSS em PNG e a Meta Graph API para publicação automática no Instagram.

```text
[Telegram Admin] ──> [Bot Telegram (Python)] ──> [Engine & Validator]
                                                       │
                                                       ▼
                                            [Playwright Renderer]
                                                       │ (HTML/CSS -> PNG 1080x1350)
                                                       ▼
[Telegram Preview + Inline Keyboard] <────────── [Preview PNG]
        │
        └─ (Ao aprovar) ──> [Meta Graph API] ──> [Post no Feed Instagram/FB]
```

---

## 2. Componentes e Módulos

* **`services/telegram_bot.py`**: Handlers de comandos, formulários e botões de aprovação no Telegram.
* **`services/renderer.py`**: Motor de captura do Playwright utilizando Jinja2 para compilar `templates/trecho_template.html` e `templates/promo_template.html`.
* **`services/meta_api.py`**: Cliente HTTP assíncrono para publicar imagens via Instagram Business / Graph API.
* **`services/ocr_extractor.py`**: Leitor OCR / IA para extração de dados caso o admin envie um screenshot da passagem/promoção.
