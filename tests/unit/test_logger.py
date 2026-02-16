import logging
from logging import Logger
import pytest
from src.infrastructure.logger import trace_performance


@pytest.mark.unit
@pytest.mark.asyncio
async def test_trace_performance_logs(caplog: pytest.LogCaptureFixture):
    @trace_performance("Test")
    async def sample():
        return "ok"

    caplog.set_level(logging.INFO)
    result = await sample()

    assert result == "ok"
    assert any(
        "[Test]" in rec.message and "Started" in rec.message for rec in caplog.records)
    assert any(
        "[Test]" in rec.message and "Finished" in rec.message for rec in caplog.records)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_trace_performance_logs_exception(caplog: pytest.LogCaptureFixture):
    @trace_performance("TestError")
    async def failing_sample():
        raise ValueError("Something went wrong")

    caplog.set_level(logging.INFO)
    with pytest.raises(ValueError, match="Something went wrong"):
        await failing_sample()

    assert any("[TestError]" in rec.message and "Started" in rec.message
               for rec in caplog.records)

    assert any("[TestError]" in rec.message and "Finished" in rec.message
               for rec in caplog.records)
