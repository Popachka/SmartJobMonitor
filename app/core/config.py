import json
from pathlib import Path
from typing import Any

from pydantic import computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
    )

    API_ID: int
    API_HASH: str
    TELEGRAM_PHONE: str | None = None
    TELETHON_LOGIN_MODE: str = "qr"
    TELEGRAM_2FA_PASSWORD: str | None = None
    BOT_TOKEN: str
    CHANNELS_MAP_PATH: str = "channels_map.json"
    MIRROR_CHANNEL: int

    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    GOOGLE_API_KEY: str
    GOOGLE_MODEL: str = 'gemini-2.5-flash'

    SENTRY_DSN: str | None = None
    SENTRY_ENV: str = "development"
    SENTRY_TRACES_SAMPLE_RATE: float = 0.0

    LOGFIRE_ENABLED: bool = True
    LOGFIRE_TOKEN: str | None = None
    LOGFIRE_SERVICE_NAME: str
    LOGFIRE_ENV: str = "development"

    METRICS_ENABLED: bool = True
    METRICS_ADDR: str = "0.0.0.0"
    METRICS_PORT: int = 8000

    @computed_field
    @property
    def ASYNC_SQLALCHEMY_DATABASE_URI(self) -> str:
        return str(
            MultiHostUrl.build(
                scheme="postgresql+asyncpg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )
        )

    @property
    def _channels_groups(self) -> dict[str, list[str]]:
        path = Path(self.CHANNELS_MAP_PATH)
        if not path.exists():
            raise FileNotFoundError(f"Channels map file not found: {path}")

        raw: Any = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("Channels map must be a JSON object")

        parsed: dict[str, list[str]] = {}
        for group_name, channels in raw.items():
            if not isinstance(group_name, str):
                raise ValueError("Channels map keys must be strings")
            if not isinstance(channels, list):
                raise ValueError(f"Group '{group_name}' must contain a list of channels")

            cleaned_channels: list[str] = []
            for channel in channels:
                if not isinstance(channel, str):
                    raise ValueError(f"Channel in group '{group_name}' must be a string")
                normalized = channel.strip()
                if normalized:
                    cleaned_channels.append(normalized)
            parsed[group_name] = cleaned_channels

        return parsed

    @computed_field
    @property
    def CHANNELS_GROUPS(self) -> dict[str, list[str]]:
        return self._channels_groups

    @computed_field
    @property
    def CHANNELS(self) -> list[str]:
        seen: set[str] = set()
        flattened: list[str] = []
        for channels in self._channels_groups.values():
            for channel in channels:
                if channel in seen:
                    continue
                seen.add(channel)
                flattened.append(channel)
        return flattened


config = Settings()
