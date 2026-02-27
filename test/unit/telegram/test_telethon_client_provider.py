import asyncio

import pytest

import app.infrastructure.telegram.telethon_client as tc


class FakeQRLogin:
    def __init__(self, client, fail_times: int = 0, raise_2fa: bool = False) -> None:
        self.url = "https://t.me/login"
        self._client = client
        self._fail_times = fail_times
        self._raise_2fa = raise_2fa
        self.wait_calls = 0
        self.recreate_calls = 0

    async def wait(self, timeout: int) -> None:
        self.wait_calls += 1
        if self._raise_2fa:
            raise tc.SessionPasswordNeededError()
        if self.wait_calls <= self._fail_times:
            raise asyncio.TimeoutError()
        self._client.authorized = True

    async def recreate(self) -> None:
        self.recreate_calls += 1


class FakeClient:
    def __init__(self, authorized: bool = False, connected: bool = False) -> None:
        self.authorized = authorized
        self.connected = connected
        self.connect_calls = 0
        self.start_calls = 0
        self.qr_login_calls = 0
        self.sign_in_calls: list[str] = []
        self.qr_login_obj: FakeQRLogin | None = None

    def is_connected(self) -> bool:
        return self.connected

    async def connect(self) -> None:
        self.connect_calls += 1
        self.connected = True

    async def is_user_authorized(self) -> bool:
        return self.authorized

    async def start(self, phone: str) -> None:
        self.start_calls += 1
        self.authorized = True

    async def qr_login(self) -> FakeQRLogin:
        self.qr_login_calls += 1
        return self.qr_login_obj

    async def sign_in(self, password: str) -> None:
        self.sign_in_calls.append(password)
        self.authorized = True

    async def disconnect(self) -> None:
        self.connected = False


@pytest.mark.asyncio
async def test_start_skips_auth_if_already_authorized(monkeypatch) -> None:
    fake_client = FakeClient(authorized=True, connected=False)
    monkeypatch.setattr(tc, "TelegramClient", lambda *_args, **_kwargs: fake_client)

    provider = tc.TelethonClientProvider("test")
    client = await provider.start()

    assert client is fake_client
    assert fake_client.connect_calls == 1
    assert fake_client.qr_login_calls == 0


@pytest.mark.asyncio
async def test_qr_login_recreates_until_success(monkeypatch) -> None:
    fake_client = FakeClient(authorized=False, connected=True)
    fake_qr = FakeQRLogin(fake_client, fail_times=1)
    fake_client.qr_login_obj = fake_qr
    monkeypatch.setattr(tc, "TelegramClient", lambda *_args, **_kwargs: fake_client)
    monkeypatch.setattr(tc.config, "TELETHON_LOGIN_MODE", "qr", raising=False)

    provider = tc.TelethonClientProvider("test")
    await provider.start()

    assert fake_client.qr_login_calls == 1
    assert fake_qr.recreate_calls == 1
    assert fake_client.authorized is True


@pytest.mark.asyncio
async def test_qr_login_uses_2fa_password(monkeypatch) -> None:
    class Fake2FAError(Exception):
        pass

    fake_client = FakeClient(authorized=False, connected=True)
    fake_qr = FakeQRLogin(fake_client, raise_2fa=True)
    fake_client.qr_login_obj = fake_qr

    monkeypatch.setattr(tc, "TelegramClient", lambda *_args, **_kwargs: fake_client)
    monkeypatch.setattr(tc, "SessionPasswordNeededError", Fake2FAError)
    monkeypatch.setattr(tc.config, "TELETHON_LOGIN_MODE", "qr", raising=False)
    monkeypatch.setattr(tc.config, "TELEGRAM_2FA_PASSWORD", "secret", raising=False)

    provider = tc.TelethonClientProvider("test")
    await provider.start()

    assert fake_client.sign_in_calls == ["secret"]
