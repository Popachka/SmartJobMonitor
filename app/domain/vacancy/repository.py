from typing import Protocol, runtime_checkable
from app.domain.vacancy.entities import Vacancy
from app.domain.vacancy.value_objects import VacancyId, ContentHash

@runtime_checkable
class IVacancyReader(Protocol):
    """Интерфейс только для чтения вакансий."""
    async def get_by_id(self, vacancy_id: VacancyId) -> Vacancy | None:
        ...

    async def get_by_content_hash(self, content_hash: ContentHash) -> Vacancy | None:
        ...

    async def exists_by_content_hash(self, content_hash: ContentHash) -> bool:
        ...

@runtime_checkable
class IVacancyRepository(Protocol):
    """Интерфейс для управления состоянием вакансий."""
    async def add(self, vacancy: Vacancy) -> None:
        """Добавить новую вакансию."""
        ...

    async def update(self, vacancy: Vacancy) -> None:
        """Обновить существующую вакансию."""
        ...

    async def upsert(self, vacancy: Vacancy) -> None:
        """Создать или обновить (например, по content_hash)."""
        ...