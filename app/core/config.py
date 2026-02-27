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
    CHANNELS: list[str]
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


config = Settings()
