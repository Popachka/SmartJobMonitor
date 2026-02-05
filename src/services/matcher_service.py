from sqlalchemy import select, func
from src.models.user import User
from src.models.vacancy import Vacancy
from sqlalchemy.ext.asyncio import AsyncSession

class MatchService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_matching_users(self, vacancy_id: int):
        # 1. Получаем стек вакансии
        vacancy_query = select(Vacancy).where(Vacancy.id == vacancy_id)
        result = await self.session.execute(vacancy_query)
        vacancy = result.scalar_one_or_none()
        
        if not vacancy or not vacancy.tech_stack:
            return []

        # 2. Ищем юзеров, у которых tech_stack пересекается со стеком вакансии
        # Используем PostgreSQL оператор ?| для JSONB
        # В SQLAlchemy это делается через func.jsonb_exists_any (если поле JSONB)
        # Или простым перебором, если данных пока мало
        
        # Для начала сделаем базовый фильтр через Python для надежности, 
        # либо используем SQL overlap если у тебя JSONB
        query = select(User).where(User.tech_stack.is_not(None))
        result = await self.session.execute(query)
        all_users = result.scalars().all()
        
        matched_users = []
        vacancy_stack = set(v.lower() for v in vacancy.tech_stack)
        
        for user in all_users:
            user_stack = set(u.lower() for u in user.tech_stack)
            if vacancy_stack.intersection(user_stack):
                matched_users.append(user)
                
        return matched_users