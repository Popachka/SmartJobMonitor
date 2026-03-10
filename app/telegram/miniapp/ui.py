from pathlib import Path

from fastapi.templating import Jinja2Templates

MINIAPP_UI_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = MINIAPP_UI_DIR / "templates"
STATIC_DIR = MINIAPP_UI_DIR / "static"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

__all__ = ["MINIAPP_UI_DIR", "STATIC_DIR", "TEMPLATES_DIR", "templates"]
