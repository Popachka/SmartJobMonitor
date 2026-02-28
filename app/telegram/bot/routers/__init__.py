from aiogram import Router

from app.telegram.bot.routers.onboarding import router as onboarding_router
from app.telegram.bot.routers.resume import router as resume_router


def get_router() -> Router:
    router = Router()
    router.include_router(onboarding_router)
    router.include_router(resume_router)
    return router
