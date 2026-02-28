from aiogram import Router

from app.telegram.bot.routers.filters import router as filters_router
from app.telegram.bot.routers.help import router as help_router
from app.telegram.bot.routers.onboarding import router as onboarding_router
from app.telegram.bot.routers.profile import router as profile_router
from app.telegram.bot.routers.resume import router as resume_router


def get_router() -> Router:
    router = Router()
    router.include_router(onboarding_router)
    router.include_router(resume_router)
    router.include_router(filters_router)
    router.include_router(profile_router)
    router.include_router(help_router)
    return router
