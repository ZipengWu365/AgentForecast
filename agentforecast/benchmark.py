from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from .backends import forecast_horizons_with_backend, is_backend_available
from .conformal import ConformalSpec
from .errors import ensure
from .features import FeatureSpec, build_feature_spec, infer_frequency_alias, list_feature_presets, prepare_series_frame


@dataclass
class BenchmarkForecastResult:
    forecast: pd.DataFrame
    predictions: dict[int, float]
    feature_spec: dict[str, Any]
    cleanup: dict[str, Any]
    diagnostics: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        forecast = self.forecast.copy()
        if "ds" in forecast.columns:
            forecast["ds"] = pd.to_datetime(forecast["ds"]).dt.strftime("%Y-%m-%d %H:%M:%S")
        return {
            "forecast": forecast.to_dict(orient="records"),
            "predictions": {str(key): value for key, value in self.predictions.items()},
            "feature_spec": self.feature_spec,
            "cleanup": self.cleanup,
            "diagnostics": self.diagnostics,
        }


def _normalize_horizons(horizon: int | None = None, horizons: list[int] | tuple[int, ...] | None = None) -> list[int]:
    raw = list(horizons or ([] if horizon is None else [horizon]))
    ensure(len(raw) > 0, "INVALID_HORIZONS", "Provide a positive horizon or a non-empty horizons list.")
    resolved = sorted({int(item) for item in raw})
    ensure(all(item > 0 for item in resolved), "INVALID_HORIZONS", "All horizons must be positive integers.")
    return resolved


def _runtime_feature_spec(
    history: pd.DataFrame,
    *,
    feature_spec: FeatureSpec | dict[str, Any] | None,
    feature_preset: str | None,
    lookback: int | None,
    benchmark_mode: bool,
    feature_clip: float | None,
    prediction_clip: float | tuple[float, float] | None,
    carry_forward_exog: bool,
) -> dict[str, Any]:
    built = build_feature_spec(
        history,
        feature_spec=feature_spec,
        feature_preset=feature_preset,
        lookback=lookback,
        benchmark_mode=benchmark_mode,
    )
    built["feature_clip"] = feature_clip
    built["prediction_clip"] = prediction_clip
    built["carry_forward_exog"] = carry_forward_exog
    return built


def _resolve_benchmark_backend(backend: str) -> tuple[str, str | None]:
    if is_backend_available(backend):
        return backend, None
    if backend == "river_linear" and is_backend_available("ml_ridge"):
        return "ml_ridge", "river_linear_requested_but_river_extra_missing; fell back to ml_ridge"
    if backend == "river_linear" and is_backend_available("stream_ewm"):
        return "stream_ewm", "river_linear_requested_but_river_extra_missing; fell back to stream_ewm"
    return backend, None


def _next_timestamp(history: pd.DataFrame, pending_future: pd.DataFrame) -> pd.Timestamp:
    if not pending_future.empty:
        return pd.Timestamp(pd.to_datetime(pending_future["ds"]).min())
    ds = pd.to_datetime(history["ds"])
    freq_alias = infer_frequency_alias(ds)
    if freq_alias:
        return pd.date_range(start=pd.Timestamp(ds.iloc[-1]), periods=2, freq=freq_alias)[1]
    if len(ds) < 2:
        return pd.Timestamp(ds.iloc[-1]) + pd.Timedelta(days=1)
    diffs = ds.diff().dropna()
    step = diffs.mode().iloc[0] if not diffs.empty else pd.Timedelta(days=1)
    return pd.Timestamp(ds.iloc[-1]) + step


def forecast_benchmark_dataframe(
    frame: pd.DataFrame,
    *,
    backend: str = "river_linear",
    horizon: int | None = None,
    horizons: list[int] | tuple[int, ...] | None = None,
    mode: str = "recursive",
    date_col: str = "ds",
    value_col: str = "y",
    series_kind: str = "auto",
    strict_mode: bool = True,
    lookback: int | None = None,
    max_history: int | None = None,
    feature_preset: str | None = "benchmark_auto",
    feature_spec: FeatureSpec | dict[str, Any] | None = None,
    conformal: ConformalSpec | None = None,
    feature_clip: float | None = None,
    prediction_clip: float | tuple[float, float] | None = None,
) -> BenchmarkForecastResult:
    resolved_horizons = _normalize_horizons(horizon=horizon, horizons=horizons)
    resolved_backend, fallback_reason = _resolve_benchmark_backend(backend)
    prepared = prepare_series_frame(
        frame,
        date_col=date_col,
        value_col=value_col,
        series_kind=series_kind,
        strict_mode=strict_mode,
        max_history=max_history,
    )
    built_feature_spec = _runtime_feature_spec(
        prepared.history,
        feature_spec=feature_spec,
        feature_preset=feature_preset,
        lookback=lookback,
        benchmark_mode=True,
        feature_clip=feature_clip,
        prediction_clip=prediction_clip,
        carry_forward_exog=not strict_mode,
    )
    forecast = forecast_horizons_with_backend(
        prepared.history,
        prepared.future_features,
        horizons=resolved_horizons,
        backend_id=resolved_backend,
        feature_spec=built_feature_spec,
        series_kind=prepared.series_kind,
        forecast_mode=mode,
        conformal=conformal,
        carry_forward_exog=not strict_mode,
    ).reset_index(drop=True)
    predictions = {int(row["horizon"]): float(row["yhat"]) for _, row in forecast.iterrows()}
    diagnostics = {
        "backend_requested": backend,
        "backend_selected": resolved_backend,
        "mode": mode,
        "strict_mode": strict_mode,
        "horizons": resolved_horizons,
        "history_len": int(len(prepared.history)),
        "future_feature_rows": int(len(prepared.future_features)),
        "carry_forward_exog": bool(not strict_mode),
    }
    if fallback_reason:
        diagnostics["fallback_reason"] = fallback_reason
    return BenchmarkForecastResult(
        forecast=forecast,
        predictions=predictions,
        feature_spec=built_feature_spec,
        cleanup=prepared.cleanup,
        diagnostics=diagnostics,
    )


class OnlineForecaster:
    def __init__(
        self,
        *,
        backend: str = "river_linear",
        horizon: int | None = None,
        horizons: list[int] | tuple[int, ...] | None = None,
        mode: str = "recursive",
        date_col: str = "ds",
        value_col: str = "y",
        series_kind: str = "auto",
        strict_mode: bool = True,
        lookback: int | None = None,
        max_history: int | None = None,
        feature_preset: str | None = "benchmark_auto",
        feature_spec: FeatureSpec | dict[str, Any] | None = None,
        conformal: ConformalSpec | None = None,
        feature_clip: float | None = None,
        prediction_clip: float | tuple[float, float] | None = None,
        allow_proxy_updates: bool = False,
    ) -> None:
        self.backend = backend
        self._resolved_backend = backend
        self.horizons = _normalize_horizons(horizon=horizon, horizons=horizons)
        self.mode = mode
        self.date_col = date_col
        self.value_col = value_col
        self.series_kind = series_kind
        self.strict_mode = strict_mode
        self.lookback = lookback
        self.max_history = max_history
        self.feature_preset = feature_preset
        self.feature_spec = feature_spec
        self.conformal = conformal
        self.feature_clip = feature_clip
        self.prediction_clip = prediction_clip
        self.allow_proxy_updates = allow_proxy_updates
        self._history: pd.DataFrame | None = None
        self._future_features: pd.DataFrame | None = None
        self._resolved_series_kind: str = series_kind
        self._built_feature_spec: dict[str, Any] | None = None
        self._cleanup: dict[str, Any] = {}
        self._audit: dict[str, Any] = {
            "fit_calls": 0,
            "predict_calls": 0,
            "update_calls": 0,
            "skipped_missing_label_updates": 0,
            "proxy_updates": 0,
        }

    def fit(self, initial_history: pd.DataFrame) -> OnlineForecaster:
        prepared = prepare_series_frame(
            initial_history,
            date_col=self.date_col,
            value_col=self.value_col,
            series_kind=self.series_kind,
            strict_mode=self.strict_mode,
            max_history=self.max_history,
        )
        self._history = prepared.history
        self._future_features = prepared.future_features
        self._resolved_series_kind = prepared.series_kind
        self._resolved_backend, fallback_reason = _resolve_benchmark_backend(self.backend)
        self._cleanup = dict(prepared.cleanup)
        if fallback_reason:
            self._cleanup["backend_fallback_reason"] = fallback_reason
        self._built_feature_spec = _runtime_feature_spec(
            prepared.history,
            feature_spec=self.feature_spec,
            feature_preset=self.feature_preset,
            lookback=self.lookback,
            benchmark_mode=True,
            feature_clip=self.feature_clip,
            prediction_clip=self.prediction_clip,
            carry_forward_exog=not self.strict_mode,
        )
        self._audit["fit_calls"] += 1
        return self

    def _require_fit(self) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
        ensure(self._history is not None, "FORECASTER_NOT_FIT", "Call fit() before predict() or update().")
        ensure(self._future_features is not None, "FORECASTER_NOT_FIT", "Call fit() before predict() or update().")
        ensure(self._built_feature_spec is not None, "FORECASTER_NOT_FIT", "Call fit() before predict() or update().")
        return self._history.copy(), self._future_features.copy(), dict(self._built_feature_spec)

    def predict(
        self,
        *,
        horizon: int | None = None,
        horizons: list[int] | tuple[int, ...] | None = None,
        future_frame: pd.DataFrame | None = None,
        as_frame: bool = False,
    ) -> dict[int, float] | pd.DataFrame:
        history, pending_future, built_feature_spec = self._require_fit()
        resolved_horizons = _normalize_horizons(horizon=horizon, horizons=horizons) if (horizon is not None or horizons is not None) else list(self.horizons)
        future_features = pending_future
        if future_frame is not None and not future_frame.empty:
            extra = future_frame.copy()
            extra[self.date_col] = pd.to_datetime(extra[self.date_col], errors="coerce")
            if self.value_col in extra.columns:
                extra = extra[extra[self.value_col].isna()].drop(columns=[self.value_col])
            extra = extra.rename(columns={self.date_col: "ds"})
            future_features = pd.concat([future_features, extra], ignore_index=True).drop_duplicates(subset=["ds"], keep="last").sort_values("ds").reset_index(drop=True)
        forecast = forecast_horizons_with_backend(
            history,
            future_features,
            horizons=resolved_horizons,
            backend_id=self._resolved_backend,
            feature_spec=built_feature_spec,
            series_kind=self._resolved_series_kind,
            forecast_mode=self.mode,
            conformal=self.conformal,
            carry_forward_exog=not self.strict_mode,
        ).reset_index(drop=True)
        self._audit["predict_calls"] += 1
        if as_frame:
            return forecast
        return {int(row["horizon"]): float(row["yhat"]) for _, row in forecast.iterrows()}

    def update(
        self,
        new_data: pd.DataFrame | dict[str, Any] | float | int,
        *,
        proxy_value: float | None = None,
    ) -> OnlineForecaster:
        history, pending_future, _ = self._require_fit()
        if isinstance(new_data, (int, float)):
            frame = pd.DataFrame(
                [
                    {
                        self.date_col: _next_timestamp(history, pending_future),
                        self.value_col: float(new_data),
                    }
                ]
            )
        elif isinstance(new_data, dict):
            frame = pd.DataFrame([new_data])
        else:
            frame = pd.DataFrame(new_data).copy()
        ensure(frame.shape[0] > 0, "EMPTY_UPDATE", "update() requires at least one row.")
        if self.date_col not in frame.columns:
            frame[self.date_col] = _next_timestamp(history, pending_future)
        frame[self.date_col] = pd.to_datetime(frame[self.date_col], errors="coerce")
        if self.value_col in frame.columns:
            frame[self.value_col] = pd.to_numeric(frame[self.value_col], errors="coerce")
        else:
            frame[self.value_col] = pd.NA

        labeled = frame[frame[self.value_col].notna()].copy()
        unlabeled = frame[frame[self.value_col].isna()].copy()

        if proxy_value is not None:
            ensure(self.allow_proxy_updates, "PROXY_UPDATE_DISABLED", "Proxy updates are disabled for this forecaster.")
            unlabeled[self.value_col] = float(proxy_value)
            labeled = pd.concat([labeled, unlabeled], ignore_index=True)
            unlabeled = unlabeled.iloc[0:0].copy()
            self._audit["proxy_updates"] += int(len(frame[frame[self.value_col].isna()]))

        if not unlabeled.empty:
            buffer = unlabeled.rename(columns={self.date_col: "ds"}).drop(columns=[self.value_col]).copy()
            pending_future = pd.concat([pending_future, buffer], ignore_index=True).drop_duplicates(subset=["ds"], keep="last").sort_values("ds").reset_index(drop=True)
            self._audit["skipped_missing_label_updates"] += int(len(unlabeled))

        if not labeled.empty:
            labeled = labeled.rename(columns={self.date_col: "ds", self.value_col: "y"})
            if "ds" in pending_future.columns:
                pending_future = pending_future[~pending_future["ds"].isin(pd.to_datetime(labeled["ds"]))].reset_index(drop=True)
            merged_history = pd.concat([history, labeled], ignore_index=True)
            prepared = prepare_series_frame(
                merged_history.rename(columns={"ds": self.date_col, "y": self.value_col}),
                date_col=self.date_col,
                value_col=self.value_col,
                series_kind=self._resolved_series_kind,
                strict_mode=self.strict_mode,
                max_history=self.max_history,
            )
            self._history = prepared.history
            self._cleanup = dict(prepared.cleanup)
            self._built_feature_spec = _runtime_feature_spec(
                prepared.history,
                feature_spec=self.feature_spec,
                feature_preset=self.feature_preset,
                lookback=self.lookback,
                benchmark_mode=True,
                feature_clip=self.feature_clip,
                prediction_clip=self.prediction_clip,
                carry_forward_exog=not self.strict_mode,
            )
        self._future_features = pending_future
        self._audit["update_calls"] += 1
        return self

    def state(self) -> dict[str, Any]:
        history_len = int(len(self._history)) if self._history is not None else 0
        pending_future = int(len(self._future_features)) if self._future_features is not None else 0
        return {
            "backend": self.backend,
            "backend_selected": self._resolved_backend,
            "horizons": list(self.horizons),
            "mode": self.mode,
            "strict_mode": self.strict_mode,
            "lookback": self.lookback,
            "max_history": self.max_history,
            "feature_preset": self.feature_preset,
            "history_len": history_len,
            "pending_future_rows": pending_future,
            "cleanup": dict(self._cleanup),
            "audit": dict(self._audit),
            "feature_spec": dict(self._built_feature_spec or {}),
        }


__all__ = [
    "BenchmarkForecastResult",
    "OnlineForecaster",
    "forecast_benchmark_dataframe",
    "list_feature_presets",
]
