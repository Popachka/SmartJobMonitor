from pathlib import Path
from typing import Any

from fastapi import Request
from fastapi.templating import Jinja2Templates

MINIAPP_UI_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = MINIAPP_UI_DIR / "templates"
STATIC_DIR = MINIAPP_UI_DIR / "static"


def _miniapp_template_context(request: Request) -> dict[str, Any]:
    def path_for(name: str, **path_params: Any) -> str:
        return str(request.app.url_path_for(name, **path_params))

    def asset_path(path: str) -> str:
        asset_file = STATIC_DIR / path
        version = int(asset_file.stat().st_mtime) if asset_file.exists() else 0
        return f"{path_for('miniapp-static', path=path)}?v={version}"

    return {
        "path_for": path_for,
        "asset_path": asset_path,
    }


templates = Jinja2Templates(
    directory=str(TEMPLATES_DIR),
    context_processors=[_miniapp_template_context],
)

__all__ = ["MINIAPP_UI_DIR", "STATIC_DIR", "TEMPLATES_DIR", "templates"]
