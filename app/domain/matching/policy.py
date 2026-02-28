from app.domain.matching.entities import MatchDecision, MatchRejectionReason
from app.domain.user.entities import User
from app.domain.user.value_objects import FilterMode
from app.domain.vacancy.entities import Vacancy


def evaluate_match(vacancy: Vacancy, user: User) -> MatchDecision:
    """Apply domain-level matching filters after repository prefilter."""
    if _rejected_by_experience(vacancy, user):
        return MatchDecision(accepted=False, reason=MatchRejectionReason.EXP)

    if _rejected_by_salary(vacancy, user):
        return MatchDecision(accepted=False, reason=MatchRejectionReason.SALARY)

    return MatchDecision(accepted=True)


def _rejected_by_experience(vacancy: Vacancy, user: User) -> bool:
    min_required = user.filter_experience_min_months
    if min_required is None:
        return False
    return vacancy.min_experience_months < min_required


def _rejected_by_salary(vacancy: Vacancy, user: User) -> bool:
    if user.filter_salary_mode != FilterMode.STRICT:
        return False
    if user.cv_salary is None or user.cv_salary.amount is None:
        return False
    if vacancy.salary.amount is None:
        return False

    user_currency = user.cv_salary.currency
    vacancy_currency = vacancy.salary.currency
    if user_currency is None or vacancy_currency is None:
        return False
    if user_currency != vacancy_currency:
        return False

    return vacancy.salary.amount < user.cv_salary.amount
