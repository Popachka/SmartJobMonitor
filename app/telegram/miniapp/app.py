from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="JobMonitor Mini App")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

app.mount("/miniapp/static", StaticFiles(directory=str(STATIC_DIR)), name="miniapp-static")


@app.get("/miniapp", include_in_schema=False)
async def miniapp_index(request: Request) -> RedirectResponse:
    return RedirectResponse(url=str(request.url_for("miniapp-specialty")), status_code=307)


@app.get("/miniapp/specialty", response_class=HTMLResponse, name="miniapp-specialty")
async def specialty_page(request: Request) -> HTMLResponse:
    context = {
        "page_title": "Специальность и язык",
        "page_description": (
            "Простой шаблон mini-app страницы для выбора направления "
            "и основного языка."
        ),
        "active_page": "specialty",
        "selected_specializations": _split_csv(request.query_params.get("specializations")),
        "selected_languages": _split_csv(request.query_params.get("primary_languages")),
        "specialization_options": ["Backend", "Frontend", "Fullstack", "DevOps"],
        "language_options": ["Python", "JavaScript"],
        "action_label": "Пока без сохранения",
    }
    return templates.TemplateResponse(
        "pages/specialty.html",
        {
            "request": request,
            **context,
        },
    )


@app.get("/miniapp/format", response_class=HTMLResponse, name="miniapp-format")
async def format_page(request: Request) -> HTMLResponse:
    current_value = (request.query_params.get("work_format_choice") or "ANY").strip().upper()
    context = {
        "page_title": "Формат работы",
        "page_description": "Базовая страница с простым выбором формата работы без сохранения.",
        "active_page": "format",
        "current_value": current_value,
        "options": [
            {"value": "ANY", "label": "Любой"},
            {"value": "REMOTE", "label": "Удаленно"},
            {"value": "HYBRID", "label": "Гибрид"},
            {"value": "ONSITE", "label": "Офис"},
        ],
        "action_label": "Применить позже",
    }
    return templates.TemplateResponse(
        "pages/format.html",
        {
            "request": request,
            **context,
        },
    )


@app.get("/miniapp/salary", response_class=HTMLResponse, name="miniapp-salary")
async def salary_page(request: Request) -> HTMLResponse:
    salary_mode = (request.query_params.get("salary_mode") or "ANY").strip().upper()
    salary_amount = (request.query_params.get("salary_amount_rub") or "").strip()
    context = {
        "page_title": "Зарплата",
        "page_description": "Шаблон экрана с минимальными полями для зарплатного фильтра.",
        "active_page": "salary",
        "salary_mode": salary_mode,
        "salary_amount": salary_amount,
        "action_label": "Сохранение появится позже",
    }
    return templates.TemplateResponse(
        "pages/salary.html",
        {
            "request": request,
            **context,
        },
    )


def _split_csv(raw_value: str | None) -> list[str]:
    if raw_value is None:
        return []
    return [item.strip() for item in raw_value.split(",") if item.strip()]
