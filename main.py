import os
import sys
import asyncio
import logging

# Configura codificação UTF-8 para o stdout no Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from config import Config
from services.telegram_bot import setup_telegram_bot
from services.renderer import renderer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

async def run_render_test():
    """Teste autônomo da renderização dos templates sem precisar do Telegram"""
    logger.info("Executando teste de renderização dos templates HTML/CSS...")
    
    trecho_data = {
        "origem_iata": "GRU",
        "origem_cidade": "São Paulo",
        "destino_iata": "MIA",
        "destino_cidade": "Miami",
        "classe": "CLASSE EXECUTIVA",
        "programa": "SMILES",
        "milhas": "55.000",
        "taxas": "180,00",
        "companhia": "American Airlines",
        "datas": "Novembro/2026",
    }
    
    promo_data = {
        "origem_programa": "LIVELO",
        "destino_programa": "LATAM PASS",
        "bonus_maximo": "100%",
        "bonus_clube": "100% de Bônus",
        "bonus_geral": "50% de Bônus",
        "min_transferencia": "10.000 pontos",
        "validade_pontos": "24 meses",
        "veredito": "EXCELENTE",
        "data_validade": "20 de Outubro"
    }

    trecho_img = await renderer.render_trecho(trecho_data)
    logger.info(f"Template Trecho renderizado com sucesso em: {trecho_img}")
    
    promo_img = await renderer.render_promo(promo_data)
    logger.info(f"Template Promoção renderizado com sucesso em: {promo_img}")

def main():
    logger.info("Iniciando Passageiro 100 Milhas Bot...")
    
    app = setup_telegram_bot()
    
    if not app:
        logger.warning("TELEGRAM_BOT_TOKEN não detectado ou inválido no arquivo .env.")
        logger.info("Rodando teste de renderização local para validar os templates visualmente...")
        asyncio.run(run_render_test())
        logger.info("Teste concluído com sucesso! Configure seu TELEGRAM_BOT_TOKEN no .env para iniciar o bot.")
    else:
        logger.info("Bot do Telegram iniciado em modo polling. Aguardando comandos...")
        app.run_polling()

if __name__ == "__main__":
    main()
