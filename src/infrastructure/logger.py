import time
import functools
import logging
import sys
from typing import Any, Callable, Coroutine, TypeVar, ParamSpec


def setup_root_logger():
    root_name = "job_monitor"
    logger = logging.getLogger(root_name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(module)s.%(funcName)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


setup_root_logger()


def get_app_logger(module_name: str):
    return logging.getLogger(f"job_monitor.{module_name}")


P = ParamSpec("P")
R = TypeVar("R")


def trace_performance(label: str):
    def decorator(func: Callable[P, Coroutine[Any, Any, R]]) -> Callable[P, Coroutine[Any, Any, R]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            module = sys.modules.get(func.__module__)
            log = getattr(module, "logger", logging.getLogger("job_monitor"))

            start_ts = time.monotonic()
            log.info(f"[{label}] — Started")

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                log.error(f"[{label}] — Failed with error: {e}")
                raise
            finally:
                duration = round(time.monotonic() - start_ts, 3)
                log.info(f"[{label}] — Finished | Duration: {duration}s")

        return wrapper
    return decorator
