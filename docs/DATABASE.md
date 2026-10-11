# 🗄️ DATABASE - Modelagem de Dados e Persistência

---

## 1. Visão Geral de Persistência no MVP

Para manter a aplicação ultraleve e compatível com as restrições de memória da VM Azure `Standard_B1s` (1 GB RAM), o **Passageiro 100 Milhas Bot (MVP)** adota uma estratégia de persistência pragmática:

1. **Estado em Trânsito (In-Memory):** As informações coletadas durante o diálogo no Telegram são mantidas temporariamente no contexto da sessão (`context.user_data` do `python-telegram-bot`).
2. **Validação Estruturada:** Esquemas Pydantic garantem a integridade dos tipos e valores antes da renderização e publicação.
3. **Mídias Temporárias (Filesystem):** As imagens PNG geradas são gravadas no diretório local `output/` com carimbo de data/hora único.

---

## 2. Esquemas de Dados Estruturados (Pydantic Schemas)

### 2.1 Modelo: Post de Alerta de Trecho (`PostTrechoData`)

```python
from typing import Optional
from pydantic import BaseModel, Field

class PostTrechoData(BaseModel):
    origem_iata: str = Field(..., min_length=3, max_length=4, description="Código IATA da origem (ex: GRU)")
    destino_iata: str = Field(..., min_length=3, max_length=4, description="Código IATA do destino (ex: MIA)")
    classe: str = Field(default="Econômica", description="Econômica, Premium Economy ou Executiva")
    companhia: str = Field(..., description="Companhia aérea operadora do voo")
    programa: str = Field(..., description="Programa de fidelidade emissor (ex: Smiles, LATAM Pass)")
    milhas: str = Field(..., description="Quantidade de milhas formatada (ex: 45.000)")
    taxas: str = Field(..., description="Valor das taxas em Reais (ex: R$ 250,00)")
    datas: str = Field(..., description="Período das datas encontradas (ex: Outubro/2026)")
    imagem_fundo_url: Optional[str] = Field(default=None, description="URL ou path local de foto de fundo customizada")
```

### 2.2 Modelo: Post de Informativo de Promoção (`PostPromoData`)

```python
from typing import Optional, List
from pydantic import BaseModel, Field

class PostPromoData(BaseModel):
    titulo_gancho: str = Field(..., description="Ex: ATÉ 100% DE BÔNUS: LIVELO ➔ LATAM PASS")
    bonus_maximo: str = Field(..., description="Ex: 100%")
    validade: str = Field(..., description="Ex: Até 15/10/2026")
    regras_basicas: List[str] = Field(default_factory=list, description="Lista de condições principais")
    analise_veredito: str = Field(..., description="Avaliação sobre a vantagem do milheiro")
    link_promocao: Optional[str] = Field(default=None, description="Link oficial da oferta")
```

---

## 3. Armazenamento de Arquivos em Disco (`output/`)

- **Convenção de Nomenclatura:**
  - `post_trecho_{YYYYMMDD_HHMMSS}_{origem}_{destino}.png`
  - `post_promo_{YYYYMMDD_HHMMSS}.png`
- **Política de Retenção:**
  - As imagens são mantidas em disco como cache de segurança para reenvio caso a API da Meta apresente instabilidade transitória.
  - Recomenda-se rotina periódica (cron semanal) para remover mídias com mais de 30 dias de criação.

---

## 4. Diretrizes para Evolução Futura (Fase 2)

Quando o projeto necessitar de histórico analítico, re-publicação e métricas, o banco de dados oficial seguirá o padrão abaixo:

### 4.1 SGBD Recomendado
- **SQLite (Inicial / Zero overhead):** Para histórico local armazenado em volume persistente Docker (`/data/bot.db`).
- **PostgreSQL (Multi-instâncias / Produção ampliada):** Para clusters ou integração com painéis analíticos externos.

### 4.2 Convenções de Nomenclatura do Banco
- **Tabelas:** Plural em `snake_case` (ex: `posts_publicados`, `historico_promocoes`, `usuarios_autorizados`).
- **Colunas:** `snake_case` (ex: `post_id`, `created_at`, `status_publicacao`).
- **Chaves Primárias:** `id` autoincremento (BigInteger) ou UUIDv4.
- **Datas:** Timestamp com fuso UTC (`created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP`).

### 4.3 Exemplo de Esquema de Tabela para Posts Publicados

```sql
CREATE TABLE IF NOT EXISTS posts_publicados (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(30) NOT NULL,              -- 'trecho' ou 'promocao'
    origem_iata VARCHAR(10),
    destino_iata VARCHAR(10),
    milhas VARCHAR(50),
    taxas VARCHAR(50),
    creation_id_meta VARCHAR(100),          -- ID do Media Container
    post_id_meta VARCHAR(100),              -- ID do post final publicado
    permalink_instagram TEXT,
    aprovado_por_telegram_id BIGINT NOT NULL,
    criado_em TIMESTAMPTZ DEFAULT NOW()
);
```

### 4.4 Migrações
- Quaisquer evoluções de schema deverão obrigatoriamente utilizar **Alembic** para versionamento de migrations.
