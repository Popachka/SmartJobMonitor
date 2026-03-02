from app.application.ports.observability_port import IObservabilityService
from app.infrastructure.observability.metrics import VACANCIES_COLLECTED_TOTAL


class PrometheusObservabilityService(IObservabilityService):
    def observe_vacancy_collected(self, count: int = 1) -> None:
        VACANCIES_COLLECTED_TOTAL.inc(count)


class NoOpObservabilityService(IObservabilityService):
    def observe_vacancy_collected(self, count: int = 1) -> None:
        return None
