"""
Tests for the health watchdog.
"""

import pytest

from src import bot
from src import health
from src.config.health import HealthConfig


class _ProcessExit(Exception):
    """
    Raised in place of os._exit so the test process survives.
    """


def _config(failures: int) -> HealthConfig:
    return HealthConfig(
        timeout_seconds=0.0,
        watchdog_enabled=True,
        watchdog_interval_seconds=0.0,
        watchdog_failures=failures,
        watchdog_startup_delay_seconds=0.0,
    )


def _raise_exit(code: int) -> None:
    raise _ProcessExit(code)


def test_watchdog_exits_after_consecutive_failures(monkeypatch) -> None:
    """
    The watchdog should exit the process once health checks fail the configured
    number of times in a row.
    """
    calls = []

    def _failing_check(_timeout: float) -> bool:
        calls.append(1)
        return False

    monkeypatch.setattr(health, "HEALTH_CONFIG", _config(failures=3))
    monkeypatch.setattr(bot, "check_health", _failing_check)
    monkeypatch.setattr(health.os, "_exit", _raise_exit)

    with pytest.raises(_ProcessExit) as exit_info:
        health.health_watchdog()

    assert exit_info.value.args == (1,)
    assert len(calls) == 3


def test_watchdog_resets_after_recovery(monkeypatch) -> None:
    """
    A successful health check should reset the failure count, so intermittent
    failures do not trigger an exit.
    """
    results = iter([False, False, True, False, False, True, False, False, False])

    def _check(_timeout: float) -> bool:
        return next(results)

    monkeypatch.setattr(health, "HEALTH_CONFIG", _config(failures=3))
    monkeypatch.setattr(bot, "check_health", _check)
    monkeypatch.setattr(health.os, "_exit", _raise_exit)

    with pytest.raises(_ProcessExit):
        health.health_watchdog()

    # The exit only happens on the final run of three consecutive failures.
    with pytest.raises(StopIteration):
        next(results)
