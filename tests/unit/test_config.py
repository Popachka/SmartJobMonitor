from src.infrastructure.config import Settings
import json
from pydantic import ValidationError
import pytest
import os
from pytest import MonkeyPatch


@pytest.fixture
def base_env(monkeypatch: MonkeyPatch) -> MonkeyPatch:
    monkeypatch.setenv("API_ID", "12345")
    monkeypatch.setenv("API_HASH", "hash")
    monkeypatch.setenv("BOT_TOKEN", "token")
    monkeypatch.setenv("CHANNELS", "[]")
    monkeypatch.setenv("MIRROR_CHANNEL", "-100123456789")
    monkeypatch.setenv("POSTGRES_USER", "postgres")
    monkeypatch.setenv("POSTGRES_SERVER", "localhost")
    monkeypatch.setenv("GOOGLE_API_KEY", "key")
    return monkeypatch


def test_settings_logic(base_env: MonkeyPatch):
    test_channels = ["@Sima", "t.me/myresume_ru", "t.me/ru_pythonjobs"]
    base_env.setenv("POSTGRES_USER", "test_user")
    base_env.setenv("CHANNELS", json.dumps(test_channels))
    cfg = Settings(_env_file=None)
    assert cfg.POSTGRES_USER == "test_user"
    assert isinstance(cfg.CHANNELS, list)
    assert len(cfg.CHANNELS) > 0
    assert cfg.CHANNELS[0] == "@Sima"


def test_database_uri_construction(base_env: MonkeyPatch):
    base_env.setenv("POSTGRES_USER", "admin")
    base_env.setenv("POSTGRES_PASSWORD", "secret")
    base_env.setenv("POSTGRES_SERVER", "db_host")
    base_env.setenv("POSTGRES_PORT", "5432")
    base_env.setenv("POSTGRES_DB", "jobs")

    cfg = Settings(_env_file=None)

    expected_uri = "postgresql+asyncpg://admin:secret@db_host:5432/jobs"
    assert cfg.ASYNC_SQLALCHEMY_DATABASE_URI == expected_uri


def test_empty_password_behavior(base_env: MonkeyPatch):
    base_env.setenv("POSTGRES_PASSWORD", "")

    cfg = Settings(_env_file=None)

    assert cfg.POSTGRES_PASSWORD == ""


def test_settings_type_validation(base_env: MonkeyPatch):
    base_env.setenv("POSTGRES_PORT", "not_a_number")

    with pytest.raises(ValidationError):
        Settings(_env_file=None)
