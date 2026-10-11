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

## 2. Identidade Visual e Paleta de Cores Institucional

A identidade visual do **Passageiro 100 Milhas** é fundamentada no estudo cromático oficial da logo da marca, combinando solidez e confiabilidade da aviação (tons de azul) com o dinamismo, agilidade e oportunidade do universo de milhas e pontos (tons de laranja).

---

### 2.1 Paleta Oficial da Marca (Estudo da Logo)

| Cor / Tom | Código HEX | Código RGB | Elemento de Origem na Logo | Uso Recomendado |
| :--- | :--- | :--- | :--- | :--- |
| **Azul Escuro** | `#003A80` | `0, 58, 128` | Texto *"Passageiro"* e Avião | Títulos, botões principais, ícones institucionais. |
| **Laranja Principal** | `#F57C00` | `245, 124, 0` | Texto *"100 Milhas"* e marcador de localização | Destaques, chamadas para ação (CTA), ícones de localização. |
| **Azul Claro** | `#0066CC` | `0, 102, 204` | Detalhes da passagem aérea / ticket | Links, subtítulos, estados de hover. |
| **Laranja Claro** | `#FFA726` | `255, 167, 38` | Detalhes do ticket | Ícones secundários, hover de botões. |
| **Cinza Claro** | `#F5F5F5` | `245, 245, 245` | Fundo neutro / sombra | Fundo de seções, cards, divisores. |

> **Análise de Harmonia & Acessibilidade:**
> - **Contraste Complementar:** A dualidade entre o Azul Escuro (`#003A80`) e o Laranja Principal (`#F57C00`) cria equilíbrio perfeito entre seriedade aeronáutica e senso de oportunidade/alerta promocional.
> - **Acessibilidade (WCAG AAA):** O contraste do texto Azul Escuro (`#003A80`) sobre o fundo Cinza Claro (`#F5F5F5`) atinge `9.5:1`, superando os padrões internacionais de legibilidade.
> - **Acentos de Interação:** O Azul Claro (`#0066CC`) e o Laranja Claro (`#FFA726`) complementam as cores primárias em microinterações, estados de hover e detalhes de hierarquia sem poluir visualmente.

---

### 2.2 Presença Digital & Link na Bio (Beacons)

Para assegurar consistência visual entre as artes do Instagram e a página de aterrissagem mobile (*link na bio*), o perfil no **Beacons** adota a identidade oficial mapeada:

#### Paleta Recomendada para o Beacons
| Elemento | Cor sugerida | Código HEX |
| :--- | :--- | :--- |
| Plano de fundo (*background*) | Cinza claro | `#F5F5F5` |
| Título e ícones principais | Azul escuro | `#003A80` |
| Botões / Call-to-action | Laranja principal | `#F57C00` |
| Hover de botões / Destaques | Laranja claro | `#FFA726` |
| Links ou texto secundário | Azul claro | `#0066CC` |

#### Mapeamento no Painel de Configuração do Beacons
| Campo no Beacons | Cor sugerida | Código HEX | Observação |
| :--- | :--- | :--- | :--- |
| `Page > Background` | Cinza claro | `#F5F5F5` | Fundo da página inteira |
| `Page > Header text and icons` | Azul escuro | `#003A80` | Títulos principais e ícones |
| `Link block > Background` | Branco (manter) | `#FFFFFF` | Fundo do bloco de link, manter claro |
| `Link block > Text` | Azul claro | `#0066CC` | Cor dos textos/links de bloco |
| `Block > Background` | Cinza claro | `#F5F5F5` | Fundo de blocos comuns |
| `Block > Text` | Azul escuro | `#003A80` | Texto dentro de blocos |
| `Block > Button background` | Laranja principal | `#F57C00` | Fundo dos botões principais |
| `Block > Button text` | Branco | `#FFFFFF` | Cor do texto dos botões |

---

### 2.3 Paleta de Aplicação no Feed do Instagram (Templates Escuros)

Nas artes gráficas geradas automaticamente para o Instagram Feed (`1080x1350px`), utiliza-se uma adaptação em modo escuro/glassmorphism de alto contraste com base na paleta oficial:

- **Acentos e Destaques (Milhas / Preço / CTAs):** Laranja Principal (`#F57C00`) com gradiente para Laranja Claro (`#FFA726`).
- **Selo Institucional e Badges:** Azul Escuro (`#003A80`) e Azul Claro (`#0066CC`).
- **Fundo Escuro (Contraste Máximo):** Preto Grafite / Azul Marinho Profundo (`#0B0F19` a `#0F172A`).
- **Overlay para Fotos:** Preto com opacidade entre 45% e 60% (`rgba(11, 15, 25, 0.55)`).
- **Texto Principal:** Branco Puro (`#FFFFFF`).
- **Texto Secundário / Labels:** Cinza Claro (`#CBD5E1` ou `#94A3B8`).
- **Selo Positivo / Sucesso:** Verde Esmeralda (`#10B981`).
- **Alerta / Urgência:** Vermelho / Coral Vivo (`#EF4444`).

---

### 2.4 Tipografia e Hierarquia Visual
- **Famílias Principais:** `Outfit` (títulos, números de milhas e destaques) e `Inter` / `Montserrat` (textos de apoio e labels).
- **Hierarquia:**
  - *Destaques / Valores (Milhas / Bônus):* Extra Bold / Black (peso 800/900), tamanho 72px a 96px.
  - *Cabeçalhos e Rotas IATA:* Bold (peso 700), tamanho 48px a 56px.
  - *Subtítulos e Taxas:* Semi-Bold / Medium (peso 500/600), tamanho 32px a 40px.
  - *Rodapés e Informações Legais:* Regular (peso 400), tamanho 22px a 26px.

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
