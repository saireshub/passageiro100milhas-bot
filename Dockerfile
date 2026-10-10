# Imagem base oficial Python 3.11 Slim
FROM python:3.11-slim

# Evita criação de arquivos .pyc e garante logs em tempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

# Instala Chromium e pacotes de fontes para renderização nítida de textos e emojis
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    fonts-liberation \
    fonts-dejavu-core \
    fonts-noto-color-emoji \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Define o caminho padrão do Chromium para o renderizador
ENV CHROMIUM_PATH=/usr/bin/chromium

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código do projeto
COPY . .

# Garante a existência do diretório de saída
RUN mkdir -p /app/output

# Executa o bot
CMD ["python", "main.py"]
