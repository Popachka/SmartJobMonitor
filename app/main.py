import asyncio

from app.bootstrap import run_application


async def main() -> None:
    await run_application()


if __name__ == "__main__":
    asyncio.run(main())
