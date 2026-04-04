from __future__ import annotations

import pytest

from agentforecast import OnlineForecaster, compare_backends_frame
from agentforecast.errors import AgentForecastError


def test_online_forecaster_strict_backend_fails_when_backend_missing(monkeypatch: pytest.MonkeyPatch, simple_frame) -> None:
    import agentforecast.backends as backends

    original = backends.is_backend_available

    def fake_is_available(backend_id: str) -> bool:
        if backend_id == "stats_arima":
            return False
        return original(backend_id)

    monkeypatch.setattr(backends, "is_backend_available", fake_is_available)

    forecaster = OnlineForecaster(backend="stats_arima", strict_backend=True)
    with pytest.raises(AgentForecastError) as exc:
        forecaster.backtest(simple_frame, horizon=7)

    assert exc.value.code == "BACKEND_UNAVAILABLE"


def test_online_forecaster_records_fallback_when_opted_in(monkeypatch: pytest.MonkeyPatch, simple_frame) -> None:
    import agentforecast.backends as backends

    original = backends.is_backend_available

    def fake_is_available(backend_id: str) -> bool:
        if backend_id == "stats_arima":
            return False
        return original(backend_id)

    monkeypatch.setattr(backends, "is_backend_available", fake_is_available)

    forecaster = OnlineForecaster(
        backend="stats_arima",
        strict_backend=False,
        allow_backend_substitution=True,
        mode="research",
    )
    payload = forecaster.backtest(simple_frame, horizon=7)

    assert payload["resolution"]["resolved_backend"] != "stats_arima"
    assert payload["resolution"]["fallback_reason"] == "requested_backend_unavailable"


def test_compare_backends_strict_mode_rejects_unavailable_requested_backend(monkeypatch: pytest.MonkeyPatch, simple_frame) -> None:
    import agentforecast.backends as backends

    original = backends.is_backend_available

    def fake_is_available(backend_id: str) -> bool:
        if backend_id == "stats_arima":
            return False
        return original(backend_id)

    monkeypatch.setattr(backends, "is_backend_available", fake_is_available)

    with pytest.raises(AgentForecastError) as exc:
        compare_backends_frame(simple_frame, name="strict_case", backends=["stats_arima", "naive"], strict_backend=True)

    assert exc.value.code == "BACKEND_UNAVAILABLE"
