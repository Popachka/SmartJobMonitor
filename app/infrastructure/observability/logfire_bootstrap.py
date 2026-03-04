import logfire

from app.core.config import config
from app.core.logger import get_app_logger

logger = get_app_logger(__name__)


def _has_logfire_token() -> bool:
    token = config.LOGFIRE_TOKEN
    return bool(token and token.strip())


def init_logfire() -> None:
    if not config.LOGFIRE_ENABLED:
        logger.info("Logfire disabled by config")
        return

    token_present = _has_logfire_token()
    if config.APP_ENV == "production" and not token_present:
        raise RuntimeError(
            "LOGFIRE_TOKEN must be set when LOGFIRE_ENABLED=true in production."
        )
    if not token_present:
        logger.warning(
            "LOGFIRE_TOKEN is empty; Logfire telemetry will not be sent to Logfire Cloud."
        )

    try:
        logfire.configure(
            send_to_logfire="if-token-present",
            token=config.LOGFIRE_TOKEN,
            service_name=config.LOGFIRE_SERVICE_NAME,
            environment=config.LOGFIRE_ENV,
        )
        logfire.instrument_pydantic_ai(
            include_content=False,
            include_binary_content=False,
        )
        logfire.instrument_system_metrics()
        logger.info("Logfire initialized")
    except Exception:
        logger.exception("Failed to initialize Logfire; continuing without it")
