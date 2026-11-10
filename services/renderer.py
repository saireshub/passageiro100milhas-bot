import os
import glob
import time
import shutil
import asyncio
import tempfile
import logging
from jinja2 import Environment, FileSystemLoader
from config import Config

logger = logging.getLogger(__name__)

class HeadlessRenderer:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader(Config.TEMPLATES_DIR), autoescape=True)
        self.chromium_binary = self._find_chromium_binary()

    def _find_chromium_binary(self) -> str:
        """Localiza o executável do Chromium / chrome-headless-shell para Windows e Linux/Docker"""
        # 1. Variável de ambiente explícita
        env_chromium = os.getenv("CHROMIUM_PATH")
        if env_chromium and os.path.exists(env_chromium):
            logger.info(f"Usando Chromium configurado em CHROMIUM_PATH: {env_chromium}")
            return env_chromium

        # 2. Caminhos padrão Linux / Docker
        linux_paths = [
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
        ]
        for path in linux_paths:
            if os.path.exists(path):
                logger.info(f"Usando Chromium Linux detectado: {path}")
                return path

        # 3. Caminhos padrão Windows
        local_app_data = os.getenv("LOCALAPPDATA", "")
        playwright_pattern = os.path.join(
            local_app_data, "ms-playwright", "chromium_headless_shell-*", "chrome-headless-shell-win64", "chrome-headless-shell.exe"
        )
        matches = glob.glob(playwright_pattern)
        if matches:
            logger.info(f"Usando Chromium Headless Shell do Playwright: {matches[0]}")
            return matches[0]

        edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        if os.path.exists(edge_path):
            logger.info(f"Usando Microsoft Edge executável: {edge_path}")
            return edge_path

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
        """Salva um HTML temporário e executa a captura headless via Chromium CLI no Linux e Windows"""
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".html", encoding="utf-8") as temp_file:
            temp_file.write(html_content)
            temp_html_path = temp_file.name

        # Diretório de perfil exclusivo para permitir que o Chromium não-root crie sua user data
        user_data_dir = tempfile.mkdtemp(prefix="chromium_ud_")

        try:
            temp_html_url = f"file:///{temp_html_path.replace(os.sep, '/')}"
            
            # Flags essenciais para containers Docker Linux headless sem servidor gráfico X11
            cmd = [
                self.chromium_binary,
                "--headless=new",
                "--no-sandbox",
                f"--user-data-dir={user_data_dir}",
                "--crash-dumps-dir=/tmp",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-software-rasterizer",
                "--hide-scrollbars",
                f"--screenshot={output_path}",
                "--window-size=1080,1350",
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
                err_text = stderr.decode("utf-8", errors="replace").strip()
                logger.warning(f"Tentativa 1 com --headless=new falhou (código {process.returncode}): {err_text}. Tentando fallback clássico...")
                
                # Fallback para Chromium usando --headless clássico
                cmd_fallback = [
                    self.chromium_binary,
                    "--headless",
                    "--no-sandbox",
                    f"--user-data-dir={user_data_dir}",
                    "--crash-dumps-dir=/tmp",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--hide-scrollbars",
                    f"--screenshot={output_path}",
                    "--window-size=1080,1350",
                    "--virtual-time-budget=2000",
                    temp_html_url
                ]
                process2 = await asyncio.create_subprocess_exec(
                    *cmd_fallback,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout2, stderr2 = await process2.communicate()
                
                if process2.returncode != 0:
                    err_text2 = stderr2.decode("utf-8", errors="replace").strip()
                    logger.error(f"Falha também no fallback Chromium CLI (código {process2.returncode}): {err_text2}")
                    raise RuntimeError(f"Falha ao gerar imagem via Chromium CLI: {err_text2 or err_text}")

            logger.info(f"Imagem gerada com sucesso em: {output_path}")

        finally:
            if os.path.exists(temp_html_path):
                try:
                    os.remove(temp_html_path)
                except Exception:
                    pass
            if os.path.exists(user_data_dir):
                try:
                    shutil.rmtree(user_data_dir, ignore_errors=True)
                except Exception:
                    pass

renderer = HeadlessRenderer()
