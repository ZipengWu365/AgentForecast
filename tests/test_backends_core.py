from __future__ import annotations

from agentforecast import backend_capabilities, list_backends, list_reviewed_backends, route_backends


def test_list_backends_exposes_support_metadata() -> None:
    backend = next(item for item in list_backends() if item["backend_id"] == "ml_ridge")
    assert backend["tier"] == "reviewed"
    assert "dependency_state" in backend
    assert backend["supports_exogenous"] is True


def test_list_reviewed_backends_matches_claim() -> None:
    reviewed_ids = {item["backend_id"] for item in list_reviewed_backends()}
    assert "stats_arima" in reviewed_ids
    assert "neural_nhits" not in reviewed_ids


def test_backend_capabilities_returns_structured_flags() -> None:
    payload = backend_capabilities("stream_ewm")
    assert payload["supports_online_update"] is True
    assert payload["strict_benchmark_eligible"] is True


def test_route_backends_returns_reason_and_candidates() -> None:
    route = route_backends(history_len=50, horizon=14, strategy="streaming", exogenous_cols=[])
    assert route["candidate_backends"]
    assert route["reason"]
