from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.application.services.user_service import UserService
from app.core.config import config
from app.domain.shared.value_objects import LanguageType, SpecializationType, WorkFormat
from app.domain.user.entities import User
from app.domain.user.value_objects import FilterMode
from app.infrastructure.db import UserUnitOfWork, async_session_factory
from app.telegram.bot.miniapp_payload import SalaryModeChoice, WorkFormatChoice
from app.telegram.miniapp.auth import MiniAppUserContext, validate_init_data

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="JobMonitor Mini App")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

app.mount("/miniapp/static", StaticFiles(directory=str(STATIC_DIR)), name="miniapp-static")


class SpecialtySaveRequest(BaseModel):
    init_data: str
    specializations: list[SpecializationType]
    primary_languages: list[LanguageType]


class FormatSaveRequest(BaseModel):
    init_data: str
    work_format_choice: WorkFormatChoice = WorkFormatChoice.ANY


class SalarySaveRequest(BaseModel):
    init_data: str
    salary_mode: SalaryModeChoice = SalaryModeChoice.ANY
    salary_amount_rub: int | None = None


@app.get("/miniapp", include_in_schema=False)
async def miniapp_index(request: Request) -> RedirectResponse:
    return RedirectResponse(url=str(request.url_for("miniapp-specialty")), status_code=307)


@app.get("/miniapp/specialty", response_class=HTMLResponse, name="miniapp-specialty")
async def specialty_page(request: Request) -> HTMLResponse:
    context = {
        "page_title": "Настройка специальностей",
        "page_description": "Добавьте или удалите нужные:",
        "active_page": "specialty",
        "selected_specializations": [],
        "selected_languages": [],
        "specialization_options": ["Backend", "Frontend", "Fullstack", "DevOps"],
        "language_options": ["Python", "JavaScript"],
        "action_label": "Сохранить",
        "save_url": str(request.url_for("miniapp-save-specialty")),
        "success_text": "Специальности сохранены.",
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
    context = {
        "page_title": "Настройка формата",
        "page_description": "Выберите подходящий формат работы:",
        "active_page": "format",
        "current_value": "",
        "options": [
            {"value": "ANY", "label": "Любой"},
            {"value": "REMOTE", "label": "Удаленно"},
            {"value": "HYBRID", "label": "Гибрид"},
            {"value": "ONSITE", "label": "Офис"},
        ],
        "action_label": "Сохранить",
        "save_url": str(request.url_for("miniapp-save-format")),
        "success_text": "Формат сохранен.",
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
    context = {
        "page_title": "Настройка зарплаты",
        "page_description": "Выберите режим зарплаты и укажите сумму при необходимости:",
        "active_page": "salary",
        "salary_mode": "",
        "salary_amount": "",
        "action_label": "Сохранить",
        "save_url": str(request.url_for("miniapp-save-salary")),
        "success_text": "Зарплата сохранена.",
    }
    return templates.TemplateResponse(
        "pages/salary.html",
        {
            "request": request,
            **context,
        },
    )


@app.get("/miniapp/api/specialty", name="miniapp-read-specialty")
async def read_specialty(request: Request) -> dict[str, list[str]]:
    user = await _get_user_from_request(request)
    return {
        "specializations": sorted(item.value for item in user.cv_specializations.items),
        "primary_languages": sorted(item.value for item in user.cv_primary_languages.items),
    }


@app.post("/miniapp/api/specialty", name="miniapp-save-specialty")
async def save_specialty(payload: SpecialtySaveRequest) -> dict[str, str]:
    user_context = _parse_user_context(payload.init_data)
    if not payload.specializations:
        raise HTTPException(status_code=400, detail="Выберите минимум одну специализацию.")
    if not payload.primary_languages:
        raise HTTPException(status_code=400, detail="Выберите минимум один основной язык.")

    service = UserService(UserUnitOfWork(async_session_factory))
    updated = await service.update_specialty_and_languages_from_miniapp(
        tg_id=user_context.tg_id,
        specializations=[item.value for item in payload.specializations],
        primary_languages=[item.value for item in payload.primary_languages],
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Пользователь не найден.")

    return {"status": "ok", "message": "Специальности сохранены."}


@app.get("/miniapp/api/format", name="miniapp-read-format")
async def read_format(request: Request) -> dict[str, str]:
    user = await _get_user_from_request(request)
    return {
        "work_format_choice": _work_format_choice(user),
    }


@app.post("/miniapp/api/format", name="miniapp-save-format")
async def save_format(payload: FormatSaveRequest) -> dict[str, str]:
    user_context = _parse_user_context(payload.init_data)

    if payload.work_format_choice == WorkFormatChoice.ANY:
        work_format = None
        work_format_mode = FilterMode.SOFT
    else:
        work_format = WorkFormat(payload.work_format_choice.value)
        work_format_mode = FilterMode.STRICT

    service = UserService(UserUnitOfWork(async_session_factory))
    updated = await service.update_work_format_from_miniapp(
        tg_id=user_context.tg_id,
        work_format=work_format,
        work_format_mode=work_format_mode,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Пользователь не найден.")

    return {"status": "ok", "message": "Формат сохранен."}


@app.get("/miniapp/api/salary", name="miniapp-read-salary")
async def read_salary(request: Request) -> dict[str, str | int | None]:
    user = await _get_user_from_request(request)
    return {
        "salary_mode": _salary_mode_choice(user),
        "salary_amount_rub": _salary_amount_value(user),
    }


@app.post("/miniapp/api/salary", name="miniapp-save-salary")
async def save_salary(payload: SalarySaveRequest) -> dict[str, str]:
    user_context = _parse_user_context(payload.init_data)

    if payload.salary_mode == SalaryModeChoice.FROM:
        if payload.salary_amount_rub is None or payload.salary_amount_rub <= 0:
            raise HTTPException(status_code=400, detail="Укажите зарплату больше 0.")
        salary_amount_rub = payload.salary_amount_rub
        salary_mode = FilterMode.STRICT
    else:
        salary_amount_rub = None
        salary_mode = FilterMode.SOFT

    service = UserService(UserUnitOfWork(async_session_factory))
    updated = await service.update_salary_from_miniapp(
        tg_id=user_context.tg_id,
        salary_amount_rub=salary_amount_rub,
        salary_mode=salary_mode,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Пользователь не найден.")

    return {"status": "ok", "message": "Зарплата сохранена."}


def _parse_user_context(init_data: str) -> MiniAppUserContext:
    try:
        return validate_init_data(init_data, config.BOT_TOKEN)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


async def _get_user_from_request(request: Request) -> User:
    init_data = request.headers.get("X-Telegram-Init-Data", "")
    user_context = _parse_user_context(init_data)
    service = UserService(UserUnitOfWork(async_session_factory))
    user = await service.get_user_by_tg_id(user_context.tg_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден.")
    return user


def _work_format_choice(user: User) -> str:
    if user.filter_work_format_mode != FilterMode.STRICT or user.cv_work_format is None:
        return WorkFormatChoice.ANY.value
    return user.cv_work_format.value


def _salary_mode_choice(user: User) -> str:
    if (
        user.filter_salary_mode == FilterMode.STRICT
        and user.cv_salary is not None
        and user.cv_salary.amount is not None
    ):
        return SalaryModeChoice.FROM.value
    return SalaryModeChoice.ANY.value


def _salary_amount_value(user: User) -> int | None:
    if user.filter_salary_mode != FilterMode.STRICT:
        return None
    if user.cv_salary is None or user.cv_salary.amount is None:
        return None
    return user.cv_salary.amount
