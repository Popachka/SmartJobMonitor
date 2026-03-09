import posixpath
from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit

from app.core.config import config
from app.domain.user.entities import User
from app.domain.user.value_objects import FilterMode
from app.telegram.bot.views.tracking_settings import format_work_format

SETTINGS_ENTRY_SPECIALTY = "specialty"
SETTINGS_ENTRY_FORMAT = "format"
SETTINGS_ENTRY_SALARY = "salary"

ENTRY_TO_PAGE = {
    SETTINGS_ENTRY_SPECIALTY: "specialty",
    SETTINGS_ENTRY_FORMAT: "format",
    SETTINGS_ENTRY_SALARY: "salary",
}


@dataclass(frozen=True, slots=True)
class SettingsMenuView:
    specialty_label: str
    format_label: str
    salary_label: str
    specialty_url: str
    format_url: str
    salary_url: str


def build_settings_menu_view(user: User) -> SettingsMenuView:
    specs_count = len(user.cv_specializations.items)
    langs_count = len(user.cv_primary_languages.items)

    specialty_label = f"Специальность и язык [{specs_count} / {langs_count}]"
    format_label = f"Формат работы [{_format_label(user)}]"
    salary_label = f"Зарплата [{_salary_label(user)}]"

    specialty_url = _build_entry_url(SETTINGS_ENTRY_SPECIALTY)
    format_url = _build_entry_url(SETTINGS_ENTRY_FORMAT)
    salary_url = _build_entry_url(SETTINGS_ENTRY_SALARY)

    return SettingsMenuView(
        specialty_label=specialty_label,
        format_label=format_label,
        salary_label=salary_label,
        specialty_url=specialty_url,
        format_url=format_url,
        salary_url=salary_url,
    )


def build_settings_menu_text() -> str:
    return (
        "⚙️ Настройки ленты вакансий\n\n"
        "Каждая inline-кнопка открывает отдельную mini-app страницу.\n"
        "Изменения сохраняются только для выбранного раздела."
    )


def _format_label(user: User) -> str:
    if user.filter_work_format_mode != FilterMode.STRICT or user.cv_work_format is None:
        return "Любой"

    rendered = format_work_format(user.cv_work_format)
    return rendered or "Любой"


def _salary_label(user: User) -> str:
    if user.filter_salary_mode != FilterMode.STRICT or user.cv_salary is None:
        return "Любая"
    if user.cv_salary.amount is None:
        return "Любая"

    amount = f"{user.cv_salary.amount:,}".replace(",", " ")
    return f"от {amount} ₽/мес"
def _build_entry_url(entry: str) -> str:
    raw_base = config.MINI_APP_BASE_URL.strip()
    if not raw_base:
        return ""

    parsed = urlsplit(raw_base)
    page = ENTRY_TO_PAGE.get(entry)
    if page is None:
        return ""

    base_dir = _resolve_base_dir(parsed.path)
    target_path = posixpath.join(base_dir, "miniapp", page)
    if not target_path.startswith("/"):
        target_path = f"/{target_path}"

    return urlunsplit(
        (
            parsed.scheme,
            parsed.netloc,
            target_path,
            "",
            parsed.fragment,
        )
    )


def _resolve_base_dir(raw_path: str) -> str:
    base_dir = raw_path or "/"
    if "." in posixpath.basename(base_dir):
        base_dir = posixpath.dirname(base_dir)
    return base_dir or "/"
