import hashlib
import hmac
import json
from dataclasses import dataclass
from urllib.parse import parse_qsl


@dataclass(frozen=True, slots=True)
class MiniAppUserContext:
    tg_id: int
    username: str | None


def validate_init_data(init_data: str, bot_token: str) -> MiniAppUserContext:
    cleaned_init_data = init_data.strip()
    if not cleaned_init_data:
        raise ValueError("Пустой initData.")

    payload = dict(parse_qsl(cleaned_init_data, keep_blank_values=True))
    received_hash = payload.pop("hash", "")
    if not received_hash:
        raise ValueError("В initData отсутствует hash.")

    data_check_string = "\n".join(
        f"{key}={value}"
        for key, value in sorted(payload.items())
    )
    secret_key = hmac.new(
        b"WebAppData",
        bot_token.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    expected_hash = hmac.new(
        secret_key,
        data_check_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(expected_hash, received_hash):
        raise ValueError("Некорректная подпись initData.")

    user_raw = payload.get("user")
    if not user_raw:
        raise ValueError("В initData отсутствуют данные пользователя.")

    try:
        user_payload = json.loads(user_raw)
    except json.JSONDecodeError as exc:
        raise ValueError("Не удалось разобрать пользователя из initData.") from exc

    if not isinstance(user_payload, dict):
        raise ValueError("Некорректный формат пользователя в initData.")

    tg_id = user_payload.get("id")
    if not isinstance(tg_id, int) or tg_id <= 0:
        raise ValueError("Некорректный Telegram user id в initData.")

    username = user_payload.get("username")
    if username is not None and not isinstance(username, str):
        raise ValueError("Некорректный username в initData.")

    return MiniAppUserContext(
        tg_id=tg_id,
        username=username,
    )
