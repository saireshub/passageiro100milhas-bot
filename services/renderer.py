import os
import glob
import time
import asyncio
import tempfile
import logging
from jinja2 import Environment, FileSystemLoader
from config import Config

logger = logging.getLogger(__name__)

class HeadlessRenderer:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader(Config.TEMPLATES_DIR))
        self.chromium_binary = self._find_chromium_binary()

    def _find_chromium_binary(self) -> str:
        """Localiza o executável do Chromium / chrome-headless-shell sem dependência de DLLs C-extensions"""
        local_app_data = os.getenv("LOCALAPPDATA", "")
        
        # 1. Procura o chrome-headless-shell instalado pelo Playwright
        playwright_pattern = os.path.join(
            local_app_data, "ms-playwright", "chromium_headless_shell-*", "chrome-headless-shell-win64", "chrome-headless-shell.exe"
        )
        matches = glob.glob(playwright_pattern)
        if matches:
            logger.info(f"Usando Chromium Headless Shell do Playwright: {matches[0]}")
            return matches[0]

        # 2. Alternativa: Microsoft Edge oficial
        edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        if os.path.exists(edge_path):
            logger.info(f"Usando Microsoft Edge executável: {edge_path}")
            return edge_path

        # 3. Alternativa: Google Chrome
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        if os.path.exists(chrome_path):
            logger.info(f"Usando Google Chrome executável: {chrome_path}")
            return chrome_path

        raise FileNotFoundError("Nenhum navegador Chromium encontrado para renderização.")

    async def render_trecho(self, data: dict) -> str:
        """Renderiza o template de Alerta de Trecho em imagem PNG (1080x1350)"""
        template = self.env.get_template("trecho_template.html")
        html_content = template.render(**data)
        
        filename = f"post_trecho_{int(time.time())}.png"
        output_path = os.path.join(Config.OUTPUT_DIR, filename)
        
        await self._capture_screenshot(html_content, output_path)
        return output_path

    async def render_promo(self, data: dict) -> str:
        """Renderiza o template de Informativo de Promoção em imagem PNG (1080x1350)"""
        template = self.env.get_template("promo_template.html")
        html_content = template.render(**data)
        
        filename = f"post_promo_{int(time.time())}.png"
        output_path = os.path.join(Config.OUTPUT_DIR, filename)
        
        await self._capture_screenshot(html_content, output_path)
        return output_path

    async def _capture_screenshot(self, html_content: str, output_path: str):
        """Salva um HTML temporário e executa a captura headless via Chromium CLI"""
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".html", encoding="utf-8") as temp_file:
            temp_file.write(html_content)
            temp_html_path = temp_file.name

        try:
            temp_html_url = f"file:///{temp_html_path.replace(os.sep, '/')}"
            
            cmd = [
                self.chromium_binary,
                f"--screenshot={output_path}",
                "--window-size=1080,1350",
                "--hide-scrollbars",
                "--disable-gpu",
                "--no-sandbox",
                "--virtual-time-budget=2000",
                "--run-all-compositor-stages-before-draw",
                temp_html_url
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                logger.error(f"Erro ao capturar screenshot via Chromium CLI: {stderr.decode()}")
                raise RuntimeError("Falha na geração da imagem via Chromium CLI")

            logger.info(f"Imagem gerada com sucesso em: {output_path}")

        finally:
            if os.path.exists(temp_html_path):
                os.remove(temp_html_path)

renderer = HeadlessRenderer()
