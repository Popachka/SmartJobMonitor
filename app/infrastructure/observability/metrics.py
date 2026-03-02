import psutil  # type: ignore[import-untyped]
from prometheus_client import Counter, Gauge

VACANCIES_COLLECTED_TOTAL = Counter(
    "job_monitor_vacancies_collected_total",
    "Total number of successfully collected vacancies since process start.",
)

PROCESS_RSS_BYTES = Gauge(
    "job_monitor_process_rss_bytes",
    "Resident set size (RSS) memory used by the current process in bytes.",
)

_PROCESS = psutil.Process()


def _current_process_rss_bytes() -> float:
    try:
        return float(_PROCESS.memory_info().rss)
    except Exception:
        return 0.0


PROCESS_RSS_BYTES.set_function(_current_process_rss_bytes)
