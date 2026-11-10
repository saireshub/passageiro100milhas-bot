# syntax=docker/dockerfile:1

# ==============================================================================
# 1. Build Stage: Compilação e isolamento do virtualenv Python
# ==============================================================================
FROM python:3.12-slim AS build
WORKDIR /src

# Cria ambiente virtual isolado
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instalação com cache mount do BuildKit e bind mount do requirements.txt
RUN --mount=type=bind,source=requirements.txt,target=requirements.txt \
    --mount=type=cache,target=/root/.cache/pip \
    pip install --no-compile -r requirements.txt

# ==============================================================================
# 2. Runtime Stage: Imagem de produção enxuta, segura e não-root
# ==============================================================================
FROM python:3.12-slim AS runtime
WORKDIR /app

# Argumento de build para rastreabilidade de versão
ARG COMMIT_SHA=development

# Variáveis de ambiente Python, Chromium e Metadados
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    CHROMIUM_PATH=/usr/bin/chromium \
    HOME=/home/appuser \
    COMMIT_SHA=${COMMIT_SHA} \
    PATH="/opt/venv/bin:$PATH"

# Instala Chromium e fontes com cache mounts do BuildKit
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    fonts-liberation \
    fonts-dejavu-core \
    fonts-noto-color-emoji \
    ca-certificates

# Criação de usuário e grupo não-root dedicados com diretório HOME e permissões temporárias
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --ingroup appgroup --home /home/appuser --disabled-password appuser && \
    mkdir -p /home/appuser /tmp/chromium-data /app/output && \
    chown -R appuser:appgroup /home/appuser /tmp/chromium-data /app/output && \
    chmod 1777 /tmp

# Copia virtualenv e código-fonte com ownership já atribuído
COPY --from=build --chown=appuser:appgroup /opt/venv /opt/venv
COPY --chown=appuser:appgroup . .

# Metadados OCI
LABEL org.opencontainers.image.title="Passageiro 100 Milhas Bot" \
      org.opencontainers.image.description="Bot Telegram e gerador de criativos para Instagram/Meta Graph API" \
      org.opencontainers.image.revision="${COMMIT_SHA}"

# Execução segura em modo não-root
USER appuser

ENTRYPOINT ["python", "main.py"]
