from app.application.ports.observability_port import IObservabilityService
from app.infrastructure.observability.metrics import (
    MESSAGES_NOT_VACANCY_TOTAL,
    SKILL_MATCHES_TOTAL,
    VACANCIES_COLLECTED_TOTAL,
)


class PrometheusObservabilityService(IObservabilityService):
    def observe_vacancy_collected(self, count: int = 1) -> None:
        VACANCIES_COLLECTED_TOTAL.inc(count)

    def observe_not_vacancy_detected(self, count: int = 1) -> None:
        MESSAGES_NOT_VACANCY_TOTAL.inc(count)

    def observe_skill_match(self, skill: str, count: int = 1) -> None:
        SKILL_MATCHES_TOTAL.labels(skill=skill).inc(count)


class NoOpObservabilityService(IObservabilityService):
    def observe_vacancy_collected(self, count: int = 1) -> None:
        return None

    def observe_not_vacancy_detected(self, count: int = 1) -> None:
        return None

    def observe_skill_match(self, skill: str, count: int = 1) -> None:
        return None
