import pytest

from app.telegram.scrapper.channels import normalize_chat_ref, normalized_channels


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (123, 123),
        ("123", "123"),
        ("-100123", "-100123"),
        ("@channel", "@channel"),
        ("channel", "@channel"),
        ("https://t.me/channel", "@channel"),
        ("http://t.me/channel", "@channel"),
        ("t.me/channel", "@channel"),
        ("  @channel  ", "@channel"),
    ],
)
def test_normalize_chat_ref(value, expected) -> None:
    assert normalize_chat_ref(value) == expected


def test_normalized_channels() -> None:
    result = normalized_channels(["t.me/a", "@b", 7])
    assert result == ["@a", "@b", 7]
