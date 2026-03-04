from app.application.ports.observability_port import IObservabilityService
from app.infrastructure.observability.metrics import (
    LANGUAGE_MATCHES_TOTAL,
    MESSAGES_NOT_VACANCY_TOTAL,
    VACANCIES_COLLECTED_TOTAL,
)


class PrometheusObservabilityService(IObservabilityService):
    def observe_vacancy_collected(self, count: int = 1) -> None:
        VACANCIES_COLLECTED_TOTAL.inc(count)

    def observe_not_vacancy_detected(self, count: int = 1) -> None:
        MESSAGES_NOT_VACANCY_TOTAL.inc(count)

    def observe_language_match(self, language: str, count: int = 1) -> None:
        LANGUAGE_MATCHES_TOTAL.labels(language=language).inc(count)


class NoOpObservabilityService(IObservabilityService):
    def observe_vacancy_collected(self, count: int = 1) -> None:
        return None

    def observe_not_vacancy_detected(self, count: int = 1) -> None:
        return None

    def observe_language_match(self, language: str, count: int = 1) -> None:
        return None
