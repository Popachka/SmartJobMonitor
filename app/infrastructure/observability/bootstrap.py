from prometheus_client import start_http_server

from app.application.ports.observability_port import IObservabilityService
from app.core.config import config
from app.core.logger import get_app_logger
from app.infrastructure.observability.service import (
    NoOpObservabilityService,
    PrometheusObservabilityService,
)

logger = get_app_logger(__name__)


def init_metrics_server() -> None:
    if not config.METRICS_ENABLED:
        logger.info("Metrics server disabled by config")
        return

    start_http_server(port=config.METRICS_PORT, addr=config.METRICS_ADDR)
    logger.info(
        "Metrics server started at %s:%s",
        config.METRICS_ADDR,
        config.METRICS_PORT,
    )


def build_observability_service() -> IObservabilityService:
    if config.METRICS_ENABLED:
        return PrometheusObservabilityService()
    return NoOpObservabilityService()
