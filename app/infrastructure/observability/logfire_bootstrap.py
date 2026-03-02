import logfire

from app.core.config import config
from app.core.logger import get_app_logger

logger = get_app_logger(__name__)


def init_logfire() -> None:
    if not config.LOGFIRE_ENABLED:
        logger.info("Logfire disabled by config")
        return

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
        logger.info("Logfire initialized")
    except Exception:
        logger.exception("Failed to initialize Logfire; continuing without it")
