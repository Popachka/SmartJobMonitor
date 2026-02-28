from app.domain.user.entities import User
from app.domain.user.value_objects import FilterMode
from app.telegram.bot.tracking_settings_view import format_salary, format_work_format


def build_search_profile_text(user: User) -> str:
    specializations = _format_specializations(user)
    languages = _format_languages(user)
    stack = _format_stack(user)

    salary = format_salary(user.cv_salary)
    work_format = format_work_format(user.cv_work_format)
    experience_text, experience_hint = _format_experience_filter(
        user.filter_experience_min_months
    )

    lines = [
        "👤 Мой профиль поиска",
        "",
        "📍 Что мы ищем:",
        _format_search_line("Направление", specializations),
        _format_search_line("Основной язык", languages),
        _format_search_line("Стек", stack),
        "",
        "⚙️ Настройки фильтров:",
        f"• Опыт: {experience_text} ({experience_hint})",
        _format_mode_filter_line(
            field_name="Зарплата",
            value=salary,
            mode=user.filter_salary_mode,
            soft_hint="Не учитываем 🟢",
            strict_hint="Скрываем всё, что меньше 🔴",
        ),
        _format_mode_filter_line(
            field_name="Формат",
            value=work_format,
            mode=user.filter_work_format_mode,
            soft_hint="Не учитываем 🟢",
            strict_hint="Только этот формат 🔴",
        ),
    ]
    return "\n".join(lines)


def _format_mode_filter_line(
    field_name: str,
    value: str | None,
    mode: FilterMode,
    soft_hint: str,
    strict_hint: str,
) -> str:
    if value is None:
        return f"• {field_name}: не найдено в резюме"
    hint = strict_hint if mode == FilterMode.STRICT else soft_hint
    return f"• {field_name}: {value} ({hint})"


def _format_search_line(field_name: str, value: str | None, suffix_emoji: str = "") -> str:
    if value is None:
        return f"• {field_name}: не найдено в резюме"
    if suffix_emoji:
        return f"• {field_name}: {value} {suffix_emoji}"
    return f"• {field_name}: {value}"


def _format_experience_filter(filter_min_months: int | None) -> tuple[str, str]:
    mapping: dict[int, str] = {
        12: "от 1 года",
        36: "от 3 лет",
        60: "от 5 лет",
    }
    if filter_min_months is None:
        return "не важен", "Не учитываем 🟢"
    if filter_min_months in mapping:
        return mapping[filter_min_months], "Скрываем всё, что меньше 🔴"
    return "не важен", "Не учитываем 🟢"


def _format_specializations(user: User) -> str | None:
    values = sorted(item.value for item in user.cv_specializations.items)
    if not values:
        return None
    return ", ".join(values)


def _format_languages(user: User) -> str | None:
    values = sorted(item.value for item in user.cv_primary_languages.items)
    if not values:
        return None
    return ", ".join(values)


def _format_stack(user: User) -> str | None:
    if user.cv_tech_stack is None or not user.cv_tech_stack.items:
        return None
    return ", ".join(sorted(user.cv_tech_stack.items))
