import asyncio
import signal
from contextlib import suppress

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.core.config import config
from app.core.logger import get_app_logger
from app.infrastructure.db import async_session_factory
from app.infrastructure.extractors.vacancy_extractor import GoogleVacancyLLMExtractor
from app.infrastructure.observability import (
    build_observability_service,
    init_logfire,
    init_metrics_server,
)
from app.infrastructure.sentry import init_sentry
from app.infrastructure.telegram.miniapp_server import (
    MiniAppServer,
    build_miniapp_server,
    run_miniapp_server,
)
from app.infrastructure.telegram.telethon_client import TelethonClientProvider
from app.telegram.bot import get_router as get_bot_router
from app.telegram.bot.commands import setup_bot_commands
from app.telegram.bot.middlewares import UserGuardMiddleware
from app.telegram.scrapper.handlers import TelegramScraper

logger = get_app_logger(__name__)


async def build_scraper(bot: Bot) -> tuple[TelegramScraper, TelethonClientProvider]:
    provider = TelethonClientProvider()
    client = await provider.start()
    extractor = GoogleVacancyLLMExtractor()
    observability = build_observability_service()
    return TelegramScraper(client, bot, async_session_factory, extractor, observability), provider


def build_bot() -> tuple[Dispatcher, Bot]:
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.message.outer_middleware(UserGuardMiddleware(async_session_factory))
    dp.include_router(get_bot_router())
    return dp, bot


def _install_shutdown_handlers(stop_event: asyncio.Event) -> list[signal.Signals]:
    loop = asyncio.get_running_loop()
    installed_signals: list[signal.Signals] = []
    for shutdown_signal in (signal.SIGINT, signal.SIGTERM):
        with suppress(NotImplementedError):
            loop.add_signal_handler(shutdown_signal, stop_event.set)
            installed_signals.append(shutdown_signal)
    return installed_signals


def _remove_shutdown_handlers(installed_signals: list[signal.Signals]) -> None:
    loop = asyncio.get_running_loop()
    for shutdown_signal in installed_signals:
        with suppress(NotImplementedError):
            loop.remove_signal_handler(shutdown_signal)


async def _shutdown_runtime(
    *,
    dp: Dispatcher,
    provider: TelethonClientProvider,
    bot: Bot,
    miniapp_server: MiniAppServer,
    scraper_task: asyncio.Task[None] | None,
    bot_task: asyncio.Task[None] | None,
    miniapp_task: asyncio.Task[None] | None,
    stop_task: asyncio.Task[bool] | None,
) -> None:
    tasks_to_await = [
        task
        for task in (scraper_task, bot_task, miniapp_task, stop_task)
        if task is not None and not task.done()
    ]

    miniapp_server.should_exit = True

    await _stop_scraper(provider)
    await _stop_bot(dp)

    if tasks_to_await:
        try:
            await asyncio.wait_for(
                asyncio.gather(*tasks_to_await, return_exceptions=True),
                timeout=10,
            )
        except TimeoutError:
            for task in tasks_to_await:
                if not task.done():
                    task.cancel()
            await asyncio.gather(*tasks_to_await, return_exceptions=True)

    await _close_bot_session(bot)


async def _stop_scraper(provider: TelethonClientProvider) -> None:
    try:
        await provider.stop()
    except Exception:
        logger.exception("Failed to stop Telethon provider during shutdown")


async def _stop_bot(dp: Dispatcher) -> None:
    try:
        await dp.stop_polling()
    except RuntimeError:
        return
    except Exception:
        logger.exception("Failed to stop bot polling during shutdown")


async def _close_bot_session(bot: Bot) -> None:
    try:
        await bot.session.close()
    except Exception:
        logger.exception("Failed to close bot session during shutdown")


async def main() -> None:
    config.validate_runtime()
    init_sentry()
    init_logfire()
    init_metrics_server()
    dp, bot = build_bot()
    await setup_bot_commands(bot)
    scraper, provider = await build_scraper(bot)
    miniapp_server = build_miniapp_server()
    stop_event = asyncio.Event()
    installed_signals = _install_shutdown_handlers(stop_event)
    scraper_task: asyncio.Task[None] | None = None
    bot_task: asyncio.Task[None] | None = None
    miniapp_task: asyncio.Task[None] | None = None
    stop_task: asyncio.Task[bool] | None = None

    try:
        scraper_task = asyncio.create_task(scraper.start(), name="scraper")
        bot_task = asyncio.create_task(
            dp.start_polling(
                bot,
                handle_signals=False,
                close_bot_session=False,
            ),
            name="telegram-bot",
        )
        miniapp_task = asyncio.create_task(
            run_miniapp_server(miniapp_server),
            name="miniapp-server",
        )
        stop_task = asyncio.create_task(stop_event.wait(), name="shutdown-signal")
        done, pending = await asyncio.wait(
            {scraper_task, bot_task, miniapp_task, stop_task},
            return_when=asyncio.FIRST_COMPLETED,
        )

        if stop_task in done:
            return

        for task in pending:
            if task is stop_task:
                task.cancel()

        completed_tasks = [task for task in done if task is not stop_task]
        for task in completed_tasks:
            exc = task.exception()
            if exc is not None:
                raise exc

        finished_names = ", ".join(task.get_name() for task in completed_tasks)
        raise RuntimeError(f"Application task exited unexpectedly: {finished_names}")
    finally:
        _remove_shutdown_handlers(installed_signals)
        await _shutdown_runtime(
            dp=dp,
            provider=provider,
            bot=bot,
            miniapp_server=miniapp_server,
            scraper_task=scraper_task,
            bot_task=bot_task,
            miniapp_task=miniapp_task,
            stop_task=stop_task,
        )


if __name__ == "__main__":
    asyncio.run(main())
