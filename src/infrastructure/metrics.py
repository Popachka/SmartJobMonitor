from __future__ import annotations

import asyncio
import time
from contextlib import asynccontextmanager
from typing import AsyncIterator

import psutil
from prometheus_client import Counter, Gauge, Histogram, start_http_server

LATENCY_SECONDS = Histogram(
    "job_monitor_latency_seconds",
    "Latency of operations in seconds",
    ["operation", "status"],
    buckets=(0.1, 0.25, 0.5, 0.75, 1, 2.5, 5, 7.5, 10, 15, 20, 30, 45, 60, 90, 120),
)
ERRORS_TOTAL = Counter(
    "job_monitor_errors_total",
    "Total number of errors",
    ["operation", "error_type"],
)
REQUESTS_TOTAL = Counter(
    "job_monitor_requests_total",
    "Total number of operations started",
    ["operation"],
)
INFLIGHT = Gauge(
    "job_monitor_inflight",
    "Number of inflight operations",
    ["operation"],
)
EVENT_LOOP_LAG_SECONDS = Gauge(
    "job_monitor_event_loop_lag_seconds",
    "Event loop lag in seconds",
)
RSS_BYTES = Gauge(
    "job_monitor_rss_bytes",
    "Resident Set Size memory in bytes",
)


class OperationTracker:
    def __init__(self, operation: str) -> None:
        self.operation = operation
        self._status = "success"
        self._start_ts = 0.0

    def start(self) -> None:
        self._start_ts = time.monotonic()
        REQUESTS_TOTAL.labels(operation=self.operation).inc()
        INFLIGHT.labels(operation=self.operation).inc()

    def mark_error(self, error: Exception) -> None:
        self._status = "error"
        ERRORS_TOTAL.labels(
            operation=self.operation,
            error_type=type(error).__name__,
        ).inc()

    def finish(self) -> None:
        duration = time.monotonic() - self._start_ts
        LATENCY_SECONDS.labels(
            operation=self.operation,
            status=self._status,
        ).observe(duration)
        INFLIGHT.labels(operation=self.operation).dec()


@asynccontextmanager
async def track(operation: str) -> AsyncIterator[OperationTracker]:
    tracker = OperationTracker(operation)
    tracker.start()
    try:
        yield tracker
    except Exception as exc:
        tracker.mark_error(exc)
        raise
    finally:
        tracker.finish()


def record_error(operation: str, error: Exception) -> None:
    ERRORS_TOTAL.labels(
        operation=operation,
        error_type=type(error).__name__,
    ).inc()


class MetricsService:
    def __init__(
        self,
        *,
        enabled: bool,
        addr: str,
        port: int,
        loop_lag_interval: float = 0.5,
        rss_interval: float = 5.0,
    ) -> None:
        self.enabled = enabled
        self.addr = addr
        self.port = port
        self.loop_lag_interval = loop_lag_interval
        self.rss_interval = rss_interval
        self._tasks: list[asyncio.Task[None]] = []
        self._started = False

    def start(self) -> None:
        if not self.enabled or self._started:
            return
        start_http_server(self.port, addr=self.addr)
        self._started = True

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return

        self._tasks.append(
            loop.create_task(
                self._track_event_loop_lag(),
                name="metrics_event_loop_lag",
            )
        )
        self._tasks.append(
            loop.create_task(
                self._track_rss_memory(),
                name="metrics_rss_memory",
            )
        )

    async def stop(self) -> None:
        if not self._tasks:
            return
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()

    async def _track_event_loop_lag(self) -> None:
        loop = asyncio.get_running_loop()
        interval = self.loop_lag_interval
        next_ts = loop.time() + interval
        while True:
            await asyncio.sleep(interval)
            now = loop.time()
            lag = max(0.0, now - next_ts)
            EVENT_LOOP_LAG_SECONDS.set(lag)
            next_ts = now + interval

    async def _track_rss_memory(self) -> None:
        process = psutil.Process()
        while True:
            try:
                RSS_BYTES.set(process.memory_info().rss)
            except Exception:
                pass
            await asyncio.sleep(self.rss_interval)
