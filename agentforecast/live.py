from __future__ import annotations

import importlib.util
from typing import Any

from .cases import _CASES, CaseSpec
from .errors import AgentForecastError
from .features import FeatureSpec
from .local import compare_backends_dataset, forecast_dataset, forecast_stream_csv
from .backends import is_backend_available
from .datasets import dataset_path


def list_cases(language: str = "en") -> list[dict[str, Any]]:
    return [case.to_dict(language) for case in _CASES]


def get_case(case_id: str, language: str = "en") -> dict[str, Any]:
    for case in _CASES:
        if case.case_id == case_id:
            return case.to_dict(language)
    raise AgentForecastError(
        code="CASE_NOT_FOUND",
        message=f"Unknown case '{case_id}'.",
        help_text="Use 'agentforecast list-cases' to inspect built-in cases.",
    )


def _case_spec(case_id: str) -> CaseSpec:
    for case in _CASES:
        if case.case_id == case_id:
            return case
    raise AgentForecastError(
        code="CASE_NOT_FOUND",
        message=f"Unknown case '{case_id}'.",
        help_text="Use 'agentforecast list-cases' to inspect built-in cases.",
    )


def _regression_lab_feature_spec() -> FeatureSpec:
    return FeatureSpec(
        mode="time_series_regression_lab",
        lag_points=(1, 2, 3, 7, 14, 21, 28),
        lag_step=7,
        lag_count=6,
        rolling_windows=(3, 7, 14, 28),
        include_tsfresh=importlib.util.find_spec("tsfresh") is not None,
        tsfresh_window=28,
        tsfresh_features=(
            "absolute_sum_of_changes",
            "autocorrelation_lag_1",
            "autocorrelation_lag_7",
            "count_above_mean",
            "longest_strike_above_mean",
            "sample_entropy",
        ),
    )


def run_case(
    case_id: str,
    *,
    outdir: str = "outputs",
    backend: str | None = None,
    strategy: str | None = None,
    live: bool = False,
    feature_spec: FeatureSpec | dict[str, Any] | None = None,
):
    case = _case_spec(case_id)
    chosen_strategy = strategy or case.default_strategy
    resolved_feature_spec = feature_spec
    if case_id == "time-series-regression-lab" and resolved_feature_spec is None:
        resolved_feature_spec = _regression_lab_feature_spec()

    if case_id == "time-series-regression-lab" and backend in {None, "auto"}:
        regression_backends = [
            backend_id
            for backend_id in ["naive", "ml_ridge", "stream_sgd", "river_linear"]
            if is_backend_available(backend_id)
        ]
        return compare_backends_dataset(
            case.dataset_id,
            backends=regression_backends,
            horizon=case.default_horizon,
            outdir=outdir,
            feature_spec=resolved_feature_spec,
        )

    if case_id in {"icu-bed-stress-watch", "beamline-drift-watch", "river-flood-risk-watch"} and backend in {None, "auto"}:
        chosen_stream = 'river_snarimax' if is_backend_available('river_snarimax') else 'stream_ewm'
        return forecast_stream_csv(
            dataset_path(case.dataset_id),
            backend=chosen_stream,
            horizon=case.default_horizon,
            outdir=outdir,
            feature_spec=resolved_feature_spec,
        )
    if case_id in {"gold-forecaster-arena", "github-breakout-radar"} and backend in {None, "auto"}:
        arena_backends = [backend_id for backend_id in ['naive', 'stats_ets', 'ml_ridge', 'stream_ewm', 'river_snarimax'] if is_backend_available(backend_id)]
        if case_id == 'gold-forecaster-arena':
            arena_backends = [backend_id for backend_id in ['naive', 'stats_arima', 'ml_ridge', 'stream_ewm', 'river_snarimax', 'statsforecast_autoarima'] if is_backend_available(backend_id)]
        return compare_backends_dataset(
            case.dataset_id,
            backends=arena_backends,
            horizon=case.default_horizon,
            outdir=outdir,
            feature_spec=resolved_feature_spec,
        )
    return forecast_dataset(
        case.dataset_id,
        horizon=case.default_horizon,
        backend=backend or "auto",
        strategy=chosen_strategy,
        outdir=outdir,
        feature_spec=resolved_feature_spec,
    )
