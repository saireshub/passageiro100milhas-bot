import os
import glob
import time
import shutil
import asyncio
import tempfile
import logging
import threading
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from config import Config
from services.storage_service import storage_service

logger = logging.getLogger(__name__)
STATE_BLOB_NAME = "state/bg_index.txt"

class HeadlessRenderer:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader(Config.TEMPLATES_DIR), autoescape=True)
        self.chromium_binary = self._find_chromium_binary()
        self._bg_index: int | None = None
        self._bg_lock = threading.Lock()
        self._local_state_file = os.path.join(Config.OUTPUT_DIR, ".bg_index")

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

    def _get_background_files(self) -> list[str]:
        """Lista as fotos de fundo em templates/assets ordenadas sequencialmente (bg_01..bg_07)"""
        assets_dir = os.path.join(Config.TEMPLATES_DIR, "assets")
        files = sorted(glob.glob(os.path.join(assets_dir, "bg_*.*")))
        return [f for f in files if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]

    def _get_next_background_uri(self) -> str | None:
        """Seleciona a próxima foto de fundo em ciclo sequencial (1 -> 7 -> 1) persistindo o índice"""
        bg_files = self._get_background_files()
        if not bg_files:
            return None

        with self._bg_lock:
            if self._bg_index is None:
                saved_val = None
                if storage_service.is_configured:
                    saved_val = storage_service.get_state_value(STATE_BLOB_NAME)
                if saved_val is None and os.path.exists(self._local_state_file):
                    try:
                        with open(self._local_state_file, "r", encoding="utf-8") as f:
                            saved_val = f.read().strip()
                    except Exception:
                        pass
                try:
                    self._bg_index = int(saved_val) % len(bg_files) if saved_val is not None else 0
                except ValueError:
                    self._bg_index = 0

            selected_path = bg_files[self._bg_index]
            logger.info(f"Foto de fundo selecionada ({self._bg_index + 1}/{len(bg_files)}): {os.path.basename(selected_path)}")

            next_index = (self._bg_index + 1) % len(bg_files)
            self._bg_index = next_index

            try:
                with open(self._local_state_file, "w", encoding="utf-8") as f:
                    f.write(str(next_index))
            except Exception:
                pass

            if storage_service.is_configured:
                storage_service.set_state_value(STATE_BLOB_NAME, str(next_index))

        return Path(selected_path).resolve().as_uri()

    async def render_trecho(self, data: dict) -> str:
        """Renderiza o template de Alerta de Trecho em imagem PNG (1080x1350)"""
        render_data = dict(data)
        if not render_data.get("imagem_fundo_url"):
            bg_uri = await asyncio.to_thread(self._get_next_background_uri)
            if bg_uri:
                render_data["imagem_fundo_url"] = bg_uri

        template = self.env.get_template("trecho_template.html")
        html_content = template.render(**render_data)
        
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

    def _build_chromium_cmd(self, headless_flag: str, user_data_dir: str, output_path: str, html_url: str) -> list[str]:
        """Monta os argumentos CLI do Chromium para renderização headless segura"""
        cmd = [
            self.chromium_binary,
            headless_flag,
            "--no-sandbox",
            "--allow-file-access-from-files",
            f"--user-data-dir={user_data_dir}",
            "--crash-dumps-dir=/tmp",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--hide-scrollbars",
            f"--screenshot={output_path}",
            "--window-size=1080,1350",
            "--virtual-time-budget=2000",
        ]
        if headless_flag == "--headless=new":
            cmd.extend(["--disable-software-rasterizer", "--run-all-compositor-stages-before-draw"])
        cmd.append(html_url)
        return cmd

    async def _run_chromium(self, cmd: list[str], timeout: float = 45.0) -> tuple[int, str]:
        """Executa o Chromium headless com timeout para evitar travamentos na captura"""
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            _, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
        except asyncio.TimeoutError as exc:
            process.kill()
            await process.wait()
            raise TimeoutError(f"Chromium headless excedeu {int(timeout)}s ao gerar a imagem.") from exc
        return process.returncode, stderr.decode("utf-8", errors="replace").strip()

    async def _capture_screenshot(self, html_content: str, output_path: str):
        """Salva um HTML temporário e executa a captura headless via Chromium CLI no Linux e Windows"""
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".html", encoding="utf-8") as temp_file:
            temp_file.write(html_content)
            temp_html_path = temp_file.name

        # Diretório de perfil exclusivo para permitir que o Chromium não-root crie sua user data
        user_data_dir = tempfile.mkdtemp(prefix="chromium_ud_")

        try:
            temp_html_url = Path(temp_html_path).resolve().as_uri()
            cmd = self._build_chromium_cmd("--headless=new", user_data_dir, output_path, temp_html_url)
            returncode, err_text = await self._run_chromium(cmd)

            if returncode != 0:
                logger.warning(f"Tentativa 1 com --headless=new falhou (código {returncode}): {err_text}. Tentando fallback clássico...")

                cmd_fallback = self._build_chromium_cmd("--headless", user_data_dir, output_path, temp_html_url)
                returncode2, err_text2 = await self._run_chromium(cmd_fallback)

                if returncode2 != 0:
                    logger.error(f"Falha também no fallback Chromium CLI (código {returncode2}): {err_text2}")
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
