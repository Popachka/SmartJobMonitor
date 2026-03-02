from typing import Protocol


class IObservabilityService(Protocol):
    def observe_vacancy_collected(self, count: int = 1) -> None: ...
