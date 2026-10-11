# 🎨 DESIGN_SYSTEM - Interface, Identidade Visual e Templates

---

## 1. Especificações Técnicas de Mídia (Instagram Feed)

Todas as imagens produzidas pelo sistema seguem estritamente as especificações otimizadas para engajamento e exibição sem cortes no feed do Instagram:

- **Dimensões:** `1080 x 1350 pixels`
- **Proporção:** `4:5` (Formato vertical com maior ocupação na tela mobile)
- **Formato de Saída:** `PNG` (renderizado sem artefatos de compressão)
- **Modo de Cor:** sRGB
- **Área Segura (Safe Zone):** Margem de 60px em todas as bordas para garantir que textos não sejam cortados por interfaces do aplicativo.

---

## 2. Tipografia e Paleta de Cores

### 2.1 Tipografia
- **Família Principal:** `Inter`, `Montserrat` ou fontes sans-serif modernas carregadas via Google Fonts nos templates HTML.
- **Hierarquia:**
  - *Destaques / Valores (Milhas / Bônus):* Extra Bold / Black (peso 800/900), tamanho 72px a 96px.
  - *Cabeçalhos e Rotas IATA:* Bold (peso 700), tamanho 48px a 56px.
  - *Subtítulos e Taxas:* Semi-Bold / Medium (peso 500/600), tamanho 32px a 40px.
  - *Rodapés e Informações Legais:* Regular (peso 400), tamanho 22px a 26px.

### 2.2 Paleta de Cores Recomendada
- **Primária (Destaque e Acentos):** Amarelo / Dourado Oportunidade (`#FFB800` ou `#F59E0B`) ou Laranja Milhas (`#FF6B00`).
- **Fundo Escuro (Contraste):** Preto Profundo / Grafite (`#0F172A` ou `#121212`).
- **Overlay para Fotos:** Preto com opacidade entre 45% e 60% (`rgba(0, 0, 0, 0.55)`).
- **Texto Principal:** Branco Puro (`#FFFFFF`).
- **Texto Secundário / Labels:** Cinza Claro (`#CBD5E1` ou `#94A3B8`).
- **Selo Positivo / Sucesso:** Verde Esmeralda (`#10B981`).
- **Alerta / Urgência:** Vermelho / Coral Vivo (`#EF4444`).

---

## 3. Linha Editorial A: Alerta de Trecho (Emissão com Milhas)

### 3.1 Composição Visual do Card
- **Fundo:** Foto da cabine ou imagem representativa do destino com gradiente linear escuro para assegurar legibilidade absoluta dos textos.
- **Cabeçalho:** Rota com códigos IATA em caixa alta (ex: `GRU ✈ MIA`) e indicação da cabine (`CLASSE EXECUTIVA`).
- **Bloco Central de Impacto:** Custo em milhas em corpo gigante (`45.000 MILHAS`) com taxas logo abaixo (`Taxas: R$ 250`).
- **Rodapé:** Logo/nome da Cia Operadora, Programa Emissor e período de datas disponíveis.

### 3.2 Template Editorial da Legenda (Instagram)

```text
🚨 ALERTA DE EMISSÃO: {origem_iata} ✈️ {destino_iata}

Classe: {classe}
Companhia Operadora: {companhia}
Programa: {programa}

💰 CUSTO POR TRECHO:
• Milhas: {milhas} milhas
• Taxas: {taxas}

📅 DATAS ENCONTRADAS:
Ida: {datas_ida}
Volta: {datas_volta}

⚠️ Dica rápida: Disponibilidade sujeita à alteração rápida pelos programas. Encontrou? Emita imediatamente!

#milhas #emissaocommilhas #passagensaereas #viagem #{programa_tag} #{destino_tag}
```

---

## 4. Linha Editorial B: Informativo de Promoção (Transferência / Bônus)

### 4.1 Composição Visual do Card
- **Estilo:** Design editorial clean, minimalista e analítico.
- **Gancho Superior:** Caixa de texto em alto contraste com o benefício máximo (ex: `ATÉ 100% DE BÔNUS: LIVELO ➔ LATAM PASS`).
- **Tabela Comparativa:** Linhas claras distinguindo percentual para assinantes de Clube vs clientes gerais e lote mínimo de transferência.
- **Selo de Avaliação:** Card com veredito (ex: `🟢 EXCELENTE OPORTUNIDADE` ou `🟡 REGULAR`).

### 4.2 Template Editorial da Legenda (Instagram)

```text
🔥 PROMOÇÃO: {parceria_origem} ➔ {parceria_destino}

Bônus máximo: até {bonus_maximo}
Validade: até {validade}

📌 REGRAS BÁSICAS:
• {bonus_clube}% para assinantes do Clube
• {bonus_geral}% para demais clientes
• Transferência mínima: {lote_minimo} pontos

💡 ANÁLISE DO PASSAGEIRO:
{analise_veredito}

🔗 Link oficial e regulamento completo no story ou link da bio.

#promocaomilhas #transferenciabonificada #livelo #smiles #latampass #esfera
```

---

## 5. Diretrizes de Implementação dos Templates HTML/CSS

- Localização: Diretório `templates/`.
- Usar tags semânticas e CSS Flexbox/Grid moderno.
- Tamanho rígido no CSS raiz:
  ```css
  body, .canvas {
      width: 1080px;
      height: 1350px;
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      overflow: hidden;
  }
  ```
- Todas as fontes web devem ser incorporadas via `@import` com fallback seguro para sans-serif.
