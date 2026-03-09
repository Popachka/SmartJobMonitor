import asyncio

from app.infrastructure.telegram.miniapp_server import run_miniapp_server


def main() -> None:
    asyncio.run(run_miniapp_server())


if __name__ == "__main__":
    main()
