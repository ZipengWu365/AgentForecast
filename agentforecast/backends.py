from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import importlib.util
import math

import numpy as np
import pandas as pd

from .conformal import ConformalSpec, attach_conformal_intervals, build_river_jackknife_wrappers, resolve_conformal_spec
from .errors import AgentForecastError, ensure
from .features import build_future_index, build_supervised_matrix, future_exog_map, infer_frequency_alias, infer_season_length, make_feature_row

DEFAULT_FEATURE_CLIP = 1_000_000.0
DEFAULT_PREDICTION_CLIP_MULTIPLIER = 20.0


@dataclass
class BackendSpec:
    backend_id: str
    family: str
    provider: str
    description: str
    extra: str
    tags: list[str]
    runtime: str = "built-in"
    notes: str | None = None

    @property
    def available(self) -> bool:
        return is_backend_available(self.backend_id)

    def to_dict(self) -> dict[str, Any]:
        return {
            "backend_id": self.backend_id,
            "family": self.family,
            "provider": self.provider,
            "description": self.description,
            "extra": self.extra,
            "available": self.available,
            "runtime": self.runtime,
            "tags": self.tags,
            "notes": self.notes,
        }


def _has(module: str) -> bool:
    try:
        return importlib.util.find_spec(module) is not None
    except ModuleNotFoundError:
        return False


_REGISTRY: dict[str, BackendSpec] = {
    # lean base path
    "naive": BackendSpec("naive", "baseline", "agentforecast", "Repeat the last observed value.", "base", ["fast", "low_data"]),
    "seasonal_naive": BackendSpec("seasonal_naive", "baseline", "agentforecast", "Repeat the most recent seasonal cycle.", "base", ["fast", "long_horizon"]),
    "moving_average": BackendSpec("moving_average", "baseline", "agentforecast", "Project the recent mean forward.", "base", ["fast"]),
    "drift": BackendSpec("drift", "baseline", "agentforecast", "Project a straight-line drift from first to last value.", "base", ["fast", "low_data"]),
    # classical
    "stats_arima": BackendSpec("stats_arima", "classical", "statsmodels", "ARIMA from statsmodels.", "stats", ["accurate", "low_data"]),
    "stats_ets": BackendSpec("stats_ets", "classical", "statsmodels", "Exponential smoothing from statsmodels.", "stats", ["accurate", "long_horizon"]),
    "statsforecast_autoarima": BackendSpec("statsforecast_autoarima", "classical", "StatsForecast", "AutoARIMA via StatsForecast.", "stats", ["accurate", "scalable"], runtime="adapter", notes="Optional adapter.") ,
    "statsforecast_autoets": BackendSpec("statsforecast_autoets", "classical", "StatsForecast", "AutoETS via StatsForecast.", "stats", ["accurate", "scalable", "long_horizon"], runtime="adapter", notes="Optional adapter."),
    # tabular
    "ml_ridge": BackendSpec("ml_ridge", "tabular", "scikit-learn", "Lag features with sklearn Ridge regression.", "ml", ["fast", "low_data", "tabular"]),
    "ml_histgb": BackendSpec("ml_histgb", "tabular", "scikit-learn", "Lag features with HistGradientBoostingRegressor.", "ml", ["accurate", "tabular"]),
    "ml_xgboost": BackendSpec("ml_xgboost", "tabular", "XGBoost", "Lag features with XGBoost.", "ml", ["accurate", "tabular"]),
    "ml_lightgbm": BackendSpec("ml_lightgbm", "tabular", "LightGBM", "Lag features with LightGBM.", "ml", ["accurate", "tabular"]),
    "ml_catboost": BackendSpec("ml_catboost", "tabular", "CatBoost", "Lag features with CatBoost.", "ml", ["accurate", "tabular"]),
    "mlforecast_linear": BackendSpec("mlforecast_linear", "tabular", "MLForecast", "MLForecast with linear regression and lag/exogenous features.", "ml", ["accurate", "tabular", "exogenous"], runtime="adapter", notes="Optional adapter."),
    "mlforecast_xgboost": BackendSpec("mlforecast_xgboost", "tabular", "MLForecast", "MLForecast with XGBoost and lag/exogenous features.", "ml", ["accurate", "tabular", "exogenous"], runtime="adapter", notes="Optional adapter."),
    # streaming / online learning
    "stream_ewm": BackendSpec("stream_ewm", "streaming", "agentforecast", "Lightweight online exponential smoothing forecaster.", "base", ["streaming", "fast", "low_data"]),
    "stream_sgd": BackendSpec("stream_sgd", "streaming", "scikit-learn", "Online SGD regression with lag features.", "ml", ["streaming", "accurate", "tabular"]),
    "river_linear": BackendSpec("river_linear", "streaming", "River", "Online linear regression with lag features in River.", "stream", ["streaming", "fast", "supports_conformal_native"], runtime="adapter"),
    "river_snarimax": BackendSpec("river_snarimax", "streaming", "River", "Online SNARIMAX forecaster in River.", "stream", ["streaming", "accurate", "supports_conformal_residual", "supports_conformal_horizon"], runtime="adapter"),
    "river_holtwinters": BackendSpec("river_holtwinters", "streaming", "River", "Online Holt-Winters forecaster in River.", "stream", ["streaming", "long_horizon", "supports_conformal_residual", "supports_conformal_horizon"], runtime="adapter"),
    # high-end optional adapters
    "neural_nhits": BackendSpec("neural_nhits", "deep", "NeuralForecast", "NHITS adapter for long-horizon deep forecasting.", "deep", ["deep", "long_horizon"], runtime="adapter", notes="Optional adapter."),
    "automl_autogluon": BackendSpec("automl_autogluon", "automl", "AutoGluon", "AutoGluon TimeSeries adapter.", "automl", ["automl", "accurate"], runtime="adapter", notes="Optional adapter."),
    "tabpfn_regression": BackendSpec("tabpfn_regression", "tabpfn", "TabPFN", "TabPFN regressor over lag features.", "tabpfn", ["tabular", "experimental"], runtime="adapter", notes="Optional adapter; check license before production use."),
}


def list_backends(*, family: str | None = None, include_unavailable: bool = True) -> list[dict[str, Any]]:
    specs = list(_REGISTRY.values())
    if family:
        specs = [spec for spec in specs if spec.family == family]
    if not include_unavailable:
        specs = [spec for spec in specs if spec.available]
    return [spec.to_dict() for spec in specs]


def list_backend_families() -> list[dict[str, Any]]:
    families: dict[str, list[str]] = {}
    for spec in _REGISTRY.values():
        families.setdefault(spec.family, []).append(spec.backend_id)
    return [{"family": family, "backends": sorted(backends)} for family, backends in sorted(families.items())]


def get_backend_spec(backend_id: str) -> BackendSpec:
    try:
        return _REGISTRY[backend_id]
    except KeyError as exc:
        raise AgentForecastError(
            code="BACKEND_NOT_FOUND",
            message=f"Unknown backend '{backend_id}'.",
            help_text="Use 'agentforecast list-backends' to inspect supported backends.",
        ) from exc


def is_backend_available(backend_id: str) -> bool:
    if backend_id in {"naive", "seasonal_naive", "moving_average", "drift", "stream_ewm"}:
        return True
    if backend_id in {"stats_arima", "stats_ets"}:
        return _has("statsmodels")
    if backend_id in {"statsforecast_autoarima", "statsforecast_autoets"}:
        return _has("statsforecast")
    if backend_id in {"ml_ridge", "ml_histgb", "stream_sgd"}:
        return _has("sklearn")
    if backend_id == "ml_xgboost":
        return _has("xgboost")
    if backend_id == "ml_lightgbm":
        return _has("lightgbm")
    if backend_id == "ml_catboost":
        return _has("catboost")
    if backend_id == "mlforecast_linear":
        return _has("mlforecast") and _has("sklearn")
    if backend_id == "mlforecast_xgboost":
        return _has("mlforecast") and _has("xgboost")
    if backend_id.startswith("river_"):
        return _has("river")
    if backend_id == "neural_nhits":
        return _has("neuralforecast")
    if backend_id == "automl_autogluon":
        return _has("autogluon.timeseries")
    if backend_id == "tabpfn_regression":
        return _has("tabpfn")
    return False


def candidate_backends(strategy: str = "fast") -> list[str]:
    strategy_map = {
        "fast": ["naive", "seasonal_naive", "moving_average", "stream_ewm", "ml_ridge", "stats_ets"],
        "accurate": ["naive", "seasonal_naive", "stats_arima", "stats_ets", "ml_ridge", "ml_xgboost", "river_snarimax", "statsforecast_autoarima", "mlforecast_linear"],
        "streaming": ["stream_ewm", "river_linear", "river_snarimax", "river_holtwinters"],
        "long_horizon": ["seasonal_naive", "stats_ets", "ml_ridge", "stream_ewm", "river_holtwinters", "neural_nhits"],
        "low_data": ["naive", "drift", "stats_arima", "stats_ets", "ml_ridge", "stream_ewm"],
    }
    chosen = strategy_map.get(strategy, strategy_map["fast"])
    return [backend for backend in chosen if is_backend_available(backend)]


def route_backends(
    *,
    history_len: int,
    horizon: int,
    strategy: str = "fast",
    exogenous_cols: list[str] | None = None,
    available_only: bool = True,
) -> dict[str, Any]:
    exogenous_cols = exogenous_cols or []
    reason_bits = []
    if history_len < 40:
        reason_bits.append("short_history_prefers_baseline_and_classical")
    if horizon >= 24:
        reason_bits.append("long_horizon_prefers_seasonal_and_smoothing_models")
    if exogenous_cols:
        reason_bits.append("exogenous_features_available")
    if strategy == "streaming":
        reason_bits.append("streaming_profile_requested")
    preferred = []
    if strategy == "streaming":
        preferred.extend(["stream_ewm", "river_snarimax", "river_linear"])
    elif strategy == "accurate":
        preferred.extend(["stats_arima", "stats_ets", "ml_ridge", "ml_xgboost", "statsforecast_autoarima"])
    elif strategy == "long_horizon":
        preferred.extend(["seasonal_naive", "stats_ets", "stream_ewm", "ml_ridge", "neural_nhits"])
    elif strategy == "low_data":
        preferred.extend(["naive", "drift", "stats_arima", "stats_ets", "stream_ewm"])
    else:
        preferred.extend(["naive", "seasonal_naive", "moving_average", "stream_ewm", "ml_ridge", "stats_ets"])

    if exogenous_cols:
        preferred.extend(['ml_ridge'])
        if strategy != 'fast':
            preferred.extend(['ml_xgboost', 'mlforecast_linear', 'mlforecast_xgboost'])

    deduped = []
    for backend_id in preferred:
        if backend_id not in deduped:
            deduped.append(backend_id)
    filtered = [bid for bid in deduped if (is_backend_available(bid) or not available_only)]
    missing = [bid for bid in deduped if bid not in filtered]
    recommended_extras = sorted({get_backend_spec(bid).extra for bid in missing if bid in _REGISTRY and get_backend_spec(bid).extra != "base"})
    return {
        "profile": strategy,
        "history_len": history_len,
        "horizon": horizon,
        "candidate_backends": filtered,
        "missing_backends": missing,
        "recommended_extras": recommended_extras,
        "reason": ", ".join(reason_bits) if reason_bits else "default_fast_path",
    }


def _future_index(history: pd.DataFrame, horizon: int) -> tuple[pd.DatetimeIndex, pd.Timedelta]:
    ds = pd.to_datetime(history["ds"])
    if len(ds) < 2:
        step = pd.Timedelta(days=1)
    else:
        diffs = ds.diff().dropna()
        step = diffs.mode().iloc[0] if not diffs.empty else pd.Timedelta(days=1)
    future_ds = build_future_index(ds, horizon, step=step)
    return future_ds, step


def _normalize_horizons(horizons: list[int] | tuple[int, ...] | None = None, *, horizon: int | None = None) -> list[int]:
    raw = list(horizons or ([] if horizon is None else [horizon]))
    ensure(len(raw) > 0, "INVALID_HORIZONS", "Provide a positive horizon or a non-empty horizons list.")
    resolved = sorted({int(item) for item in raw})
    ensure(all(item > 0 for item in resolved), "INVALID_HORIZONS", "All horizons must be positive integers.")
    return resolved


def _runtime_option(feature_spec: dict[str, Any], key: str, default: Any) -> Any:
    return feature_spec.get(key, default)


def _sanitize_feature_frame(frame: pd.DataFrame, *, feature_spec: dict[str, Any]) -> pd.DataFrame:
    clip_value = _runtime_option(feature_spec, "feature_clip", DEFAULT_FEATURE_CLIP)
    clip_value = DEFAULT_FEATURE_CLIP if clip_value is None else float(clip_value)
    array = frame.to_numpy(dtype=float, copy=True)
    array = np.nan_to_num(array, nan=0.0, posinf=clip_value, neginf=-clip_value)
    array = np.clip(array, -clip_value, clip_value)
    return pd.DataFrame(array, columns=frame.columns)


def _sanitize_feature_dict(values: dict[str, float], *, feature_spec: dict[str, Any]) -> dict[str, float]:
    clip_value = _runtime_option(feature_spec, "feature_clip", DEFAULT_FEATURE_CLIP)
    clip_value = DEFAULT_FEATURE_CLIP if clip_value is None else float(clip_value)
    sanitized: dict[str, float] = {}
    for key, value in values.items():
        numeric = float(value)
        if not np.isfinite(numeric):
            numeric = 0.0
        sanitized[key] = float(np.clip(numeric, -clip_value, clip_value))
    return sanitized


def _prediction_clip_bounds(y_history: list[float], prediction_clip: Any) -> tuple[float, float]:
    if prediction_clip is None:
        scale = max(float(np.nanmax(np.abs(np.asarray(y_history, dtype=float)))), 1.0) if y_history else 1.0
        bound = max(scale * DEFAULT_PREDICTION_CLIP_MULTIPLIER, 1.0)
        return -bound, bound
    if isinstance(prediction_clip, (list, tuple)) and len(prediction_clip) == 2:
        return float(prediction_clip[0]), float(prediction_clip[1])
    bound = abs(float(prediction_clip))
    return -bound, bound


def _fallback_prediction(y_history: list[float]) -> float:
    if not y_history:
        return 0.0
    for value in reversed(y_history):
        numeric = float(value)
        if np.isfinite(numeric):
            return numeric
    return 0.0


def _sanitize_prediction(value: float, y_history: list[float], *, feature_spec: dict[str, Any]) -> float:
    numeric = float(value)
    if not np.isfinite(numeric):
        numeric = _fallback_prediction(y_history)
    lower, upper = _prediction_clip_bounds(y_history, _runtime_option(feature_spec, "prediction_clip", None))
    numeric = float(np.clip(numeric, lower, upper))
    if not np.isfinite(numeric):
        numeric = _fallback_prediction(y_history)
    return numeric


def supports_direct_forecast(backend_id: str) -> bool:
    return backend_id in {
        "ml_ridge",
        "ml_histgb",
        "ml_xgboost",
        "ml_lightgbm",
        "ml_catboost",
        "river_linear",
        "tabpfn_regression",
    }


def _freq_alias(history: pd.DataFrame) -> str:
    ds = pd.to_datetime(history["ds"])
    inferred = infer_frequency_alias(ds)
    if inferred:
        return inferred
    if len(ds) < 2:
        return "D"
    step = ds.diff().dropna().mode().iloc[0]
    if step == pd.Timedelta(hours=1):
        return "H"
    if step == pd.Timedelta(days=1):
        return "D"
    if step == pd.Timedelta(days=7):
        return "W"
    return "D"


def _attach_intervals(
    forecast: pd.DataFrame,
    residuals: np.ndarray,
    series_kind: str,
    *,
    backend_id: str,
    conformal: ConformalSpec | None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    return attach_conformal_intervals(
        forecast,
        spec=conformal,
        residuals=residuals,
        series_kind=series_kind,
        backend_id=backend_id,
    )


def _seasonal_length(history: pd.DataFrame) -> int | None:
    ds = pd.to_datetime(history["ds"])
    step = ds.diff().dropna().mode().iloc[0] if len(ds) > 1 else pd.Timedelta(days=1)
    return infer_season_length(step, freq_alias=infer_frequency_alias(ds))


def _forecast_baseline(history: pd.DataFrame, horizon: int, backend_id: str) -> pd.DataFrame:
    y = history["y"].astype(float).to_numpy()
    future_ds, _ = _future_index(history, horizon)
    season_length = _seasonal_length(history)
    if backend_id == "naive":
        yhat = np.repeat(y[-1], horizon)
    elif backend_id == "moving_average":
        window = min(7, len(y))
        yhat = np.repeat(float(np.mean(y[-window:])), horizon)
    elif backend_id == "drift":
        slope = float((y[-1] - y[0]) / max(len(y) - 1, 1))
        yhat = y[-1] + slope * np.arange(1, horizon + 1)
    elif backend_id == "seasonal_naive" and season_length:
        recent = y[-season_length:]
        reps = int(np.ceil(horizon / season_length))
        yhat = np.tile(recent, reps)[:horizon]
    else:
        raise AgentForecastError(code="UNSUPPORTED_BASELINE", message=f"Baseline backend '{backend_id}' is not supported.")
    return pd.DataFrame({"ds": future_ds, "yhat": yhat.astype(float)})


def _forecast_stats(history: pd.DataFrame, horizon: int, backend_id: str) -> pd.DataFrame:
    y = history["y"].astype(float).to_numpy()
    future_ds, _ = _future_index(history, horizon)
    season_length = _seasonal_length(history) or 1
    if backend_id == "stats_arima":
        from statsmodels.tsa.arima.model import ARIMA
        order = (1, 1, 1) if len(y) >= 20 else (1, 0, 1)
        model = ARIMA(y, order=order)
        fit = model.fit()
        pred = fit.forecast(steps=horizon)
        yhat = np.asarray(pred, dtype=float)
    elif backend_id == "stats_ets":
        from statsmodels.tsa.holtwinters import ExponentialSmoothing
        seasonal = "add" if season_length and len(y) >= season_length * 2 else None
        trend = "add" if len(y) >= 8 else None
        model = ExponentialSmoothing(y, trend=trend, seasonal=seasonal, seasonal_periods=season_length if seasonal else None)
        fit = model.fit(optimized=True)
        pred = fit.forecast(horizon)
        yhat = np.asarray(pred, dtype=float)
    else:
        raise AgentForecastError(code="UNSUPPORTED_STATS_BACKEND", message=f"Stats backend '{backend_id}' is not supported.")
    return pd.DataFrame({"ds": future_ds, "yhat": yhat})


def _forecast_statsforecast(history: pd.DataFrame, horizon: int, backend_id: str) -> pd.DataFrame:
    from statsforecast import StatsForecast
    from statsforecast.models import AutoARIMA, AutoETS

    models = {
        "statsforecast_autoarima": AutoARIMA(season_length=_seasonal_length(history) or 1),
        "statsforecast_autoets": AutoETS(season_length=_seasonal_length(history) or 1),
    }
    df = history[["ds", "y"]].copy()
    df["unique_id"] = "series"
    sf = StatsForecast(models=[models[backend_id]], freq=_freq_alias(history))
    pred = sf.forecast(df=df, h=horizon)
    future_ds, _ = _future_index(history, horizon)
    value_col = [col for col in pred.columns if col not in {"ds", "unique_id"}][0]
    return pd.DataFrame({"ds": future_ds, "yhat": pred[value_col].to_numpy(dtype=float)})


def _fit_sklearn_regression(backend_id: str):
    if backend_id in {"ml_ridge", "mlforecast_linear"}:
        from sklearn.linear_model import Ridge
        return Ridge(alpha=1.0)
    if backend_id == "ml_histgb":
        from sklearn.ensemble import HistGradientBoostingRegressor
        return HistGradientBoostingRegressor(max_depth=4, learning_rate=0.06, max_iter=200, random_state=0)
    if backend_id in {"ml_xgboost", "mlforecast_xgboost"}:
        from xgboost import XGBRegressor
        return XGBRegressor(
            n_estimators=140,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="reg:squarederror",
            random_state=0,
            verbosity=0,
        )
    if backend_id == "ml_lightgbm":
        from lightgbm import LGBMRegressor
        return LGBMRegressor(n_estimators=120, learning_rate=0.05, max_depth=4, random_state=0)
    if backend_id == "ml_catboost":
        from catboost import CatBoostRegressor
        return CatBoostRegressor(iterations=180, depth=6, learning_rate=0.05, loss_function="RMSE", verbose=False, random_seed=0)
    raise AgentForecastError(code="UNSUPPORTED_ML_BACKEND", message=f"ML backend '{backend_id}' is not supported.")


def _forecast_tabular(
    history: pd.DataFrame,
    future_features_df: pd.DataFrame,
    horizon: int,
    backend_id: str,
    feature_spec: dict[str, Any],
) -> pd.DataFrame:
    X, y = build_supervised_matrix(history, feature_spec=feature_spec)
    X = _sanitize_feature_frame(X, feature_spec=feature_spec)
    model = _fit_sklearn_regression(backend_id)
    model.fit(X, y)
    future_ds, step = _future_index(history, horizon)
    y_history = history["y"].astype(float).tolist()
    exog_cols = feature_spec.get("exogenous_cols", [])
    exog_future = future_exog_map(
        history,
        future_features_df,
        horizon=horizon,
        step=step,
        exogenous_cols=exog_cols,
        carry_forward=bool(feature_spec.get("carry_forward_exog", True)),
    )
    preds: list[float] = []
    for ds, exog in zip(future_ds, exog_future):
        feats = _sanitize_feature_dict(make_feature_row(pd.Timestamp(ds), y_history, feature_spec=feature_spec, exog_values=exog), feature_spec=feature_spec)
        x = _sanitize_feature_frame(pd.DataFrame([feats]).fillna(0.0), feature_spec=feature_spec)
        yhat = _sanitize_prediction(float(model.predict(x)[0]), y_history, feature_spec=feature_spec)
        preds.append(yhat)
        y_history.append(yhat)
    return pd.DataFrame({"ds": future_ds, "yhat": np.asarray(preds, dtype=float)})


def _forecast_mlforecast(
    history: pd.DataFrame,
    future_features_df: pd.DataFrame,
    horizon: int,
    backend_id: str,
    feature_spec: dict[str, Any],
) -> pd.DataFrame:
    from mlforecast import MLForecast

    model = _fit_sklearn_regression(backend_id)
    df = history.copy()
    df = df.rename(columns={"ds": "ds", "y": "y"})
    df["unique_id"] = "series"
    lags = list(feature_spec.get("lags", [1, 2, 3]))
    fcst = MLForecast(models=[model], freq=_freq_alias(history), lags=lags)
    static_features: list[str] = []
    fcst.fit(df=df[["unique_id", "ds", "y"] + feature_spec.get("exogenous_cols", [])], static_features=static_features)
    exog_cols = feature_spec.get("exogenous_cols", [])
    if exog_cols:
        future_ds, step = _future_index(history, horizon)
        exog_rows = future_exog_map(
            history,
            future_features_df,
            horizon=horizon,
            step=step,
            exogenous_cols=exog_cols,
            carry_forward=bool(feature_spec.get("carry_forward_exog", True)),
        )
        X_df = pd.DataFrame({"unique_id": "series", "ds": future_ds})
        for col in exog_cols:
            X_df[col] = [row.get(col, float(history[col].iloc[-1])) for row in exog_rows]
    else:
        X_df = None
    pred = fcst.predict(h=horizon, X_df=X_df)
    value_col = [col for col in pred.columns if col not in {"ds", "unique_id"}][0]
    return pd.DataFrame({"ds": pd.to_datetime(pred["ds"]), "yhat": pred[value_col].to_numpy(dtype=float)})


def _forecast_stream_builtin(
    history: pd.DataFrame,
    future_features_df: pd.DataFrame,
    horizon: int,
    backend_id: str,
    feature_spec: dict[str, Any],
) -> pd.DataFrame:
    future_ds, step = _future_index(history, horizon)
    y = history["y"].astype(float).tolist()
    exog_cols = feature_spec.get("exogenous_cols", [])
    exog_future = future_exog_map(
        history,
        future_features_df,
        horizon=horizon,
        step=step,
        exogenous_cols=exog_cols,
        carry_forward=bool(feature_spec.get("carry_forward_exog", True)),
    )

    if backend_id == "stream_ewm":
        alpha = 0.35
        level = float(y[0])
        trend = float(y[1] - y[0]) if len(y) > 1 else 0.0
        for idx in range(1, len(y)):
            new_level = alpha * y[idx] + (1 - alpha) * (level + trend)
            trend = 0.15 * (new_level - level) + (1 - 0.15) * trend
            level = new_level
        preds = []
        local_level, local_trend = level, trend
        for step_idx in range(1, horizon + 1):
            yhat = _sanitize_prediction(local_level + step_idx * local_trend, y, feature_spec=feature_spec)
            preds.append(float(yhat))
        return pd.DataFrame({"ds": future_ds, "yhat": np.asarray(preds, dtype=float)})

    if backend_id == "stream_sgd":
        from sklearn.linear_model import SGDRegressor

        model = SGDRegressor(random_state=0, max_iter=1, tol=None, learning_rate="invscaling")
        y_history: list[float] = []
        is_fit = False
        records = history.to_dict("records")
        max_lag = max(feature_spec.get("lags", [1]))
        for ds_i, row in zip(pd.to_datetime(history["ds"]), records):
            y_i = float(row["y"])
            if len(y_history) >= max_lag:
                exog = {col: float(row[col]) for col in exog_cols}
                feats = _sanitize_feature_dict(make_feature_row(pd.Timestamp(ds_i), y_history, feature_spec=feature_spec, exog_values=exog), feature_spec=feature_spec)
                x = _sanitize_feature_frame(pd.DataFrame([feats]).fillna(0.0), feature_spec=feature_spec)
                if not is_fit:
                    model.partial_fit(x, np.asarray([y_i], dtype=float))
                    is_fit = True
                else:
                    model.partial_fit(x, np.asarray([y_i], dtype=float))
            y_history.append(y_i)
        if not is_fit:
            return _forecast_baseline(history, horizon, "naive")
        preds: list[float] = []
        full_history = y.copy()
        for ds_i, exog in zip(future_ds, exog_future):
            feats = _sanitize_feature_dict(make_feature_row(pd.Timestamp(ds_i), full_history, feature_spec=feature_spec, exog_values=exog), feature_spec=feature_spec)
            x = _sanitize_feature_frame(pd.DataFrame([feats]).fillna(0.0), feature_spec=feature_spec)
            yhat = _sanitize_prediction(float(model.predict(x)[0]), full_history, feature_spec=feature_spec)
            preds.append(yhat)
            full_history.append(yhat)
        return pd.DataFrame({"ds": future_ds, "yhat": np.asarray(preds, dtype=float)})

    raise AgentForecastError(code="UNSUPPORTED_STREAM_BACKEND", message=f"Streaming backend '{backend_id}' is not supported.")


def _river_calendar_x(ds: pd.Timestamp) -> dict[str, float]:
    return {
        "ordinal": float(ds.toordinal()),
        "dayofweek": float(ds.dayofweek),
        "month": float(ds.month),
        "dayofyear": float(ds.dayofyear),
        "sin_dayofyear": math.sin(2 * math.pi * ds.dayofyear / 365.25),
        "cos_dayofyear": math.cos(2 * math.pi * ds.dayofyear / 365.25),
    }


def _forecast_river(
    history: pd.DataFrame,
    future_features_df: pd.DataFrame,
    horizon: int,
    backend_id: str,
    feature_spec: dict[str, Any],
    conformal: ConformalSpec | None = None,
) -> pd.DataFrame:
    if backend_id == "river_linear" and not _has("river"):
        return _forecast_tabular(history, future_features_df, horizon, "ml_ridge", feature_spec)

    from river import linear_model, preprocessing, optim, time_series

    ds = pd.to_datetime(history["ds"])
    y = history["y"].astype(float).tolist()
    future_ds, step = _future_index(history, horizon)
    season_length = _seasonal_length(history) or 1
    exog_cols = feature_spec.get("exogenous_cols", [])
    exog_future = future_exog_map(
        history,
        future_features_df,
        horizon=horizon,
        step=step,
        exogenous_cols=exog_cols,
        carry_forward=bool(feature_spec.get("carry_forward_exog", True)),
    )

    if backend_id == "river_linear":
        effective_spec = resolve_conformal_spec(conformal, preserve_legacy_levels=conformal is None)

        def _regressor_factory():
            return preprocessing.StandardScaler() | linear_model.LinearRegression(optimizer=optim.Adam(0.001))

        use_jackknife = effective_spec.enabled and effective_spec.method in {"auto", "river_jackknife"}
        model = _regressor_factory()
        jackknife_models = (
            build_river_jackknife_wrappers(
                regressor_factory=_regressor_factory,
                levels=effective_spec.levels,
                calibration_window=effective_spec.calibration_window,
            )
            if use_jackknife
            else {}
        )
        y_history: list[float] = []
        trained_examples = 0
        for ds_i, y_i, row in zip(ds, y, history.to_dict("records")):
            if len(y_history) >= max(feature_spec.get("lags", [1])):
                exog = {col: float(row[col]) for col in exog_cols}
                feats = _sanitize_feature_dict(make_feature_row(pd.Timestamp(ds_i), y_history, feature_spec=feature_spec, exog_values=exog), feature_spec=feature_spec)
                model.learn_one(feats, y_i)
                for wrapped in jackknife_models.values():
                    wrapped.learn_one(feats, y_i)
                trained_examples += 1
            y_history.append(float(y_i))
        preds: list[float] = []
        interval_bounds: dict[int, tuple[list[float], list[float]]] = {
            level: ([], []) for level in effective_spec.levels
        }
        full_history = y.copy()
        for ds_i, exog in zip(future_ds, exog_future):
            feats = _sanitize_feature_dict(make_feature_row(pd.Timestamp(ds_i), full_history, feature_spec=feature_spec, exog_values=exog), feature_spec=feature_spec)
            yhat = _sanitize_prediction(float(model.predict_one(feats) or full_history[-1]), full_history, feature_spec=feature_spec)
            preds.append(yhat)
            if jackknife_models and trained_examples >= effective_spec.warmup_min:
                for level, wrapped in jackknife_models.items():
                    interval = wrapped.predict_one(feats, with_interval=True)
                    lower = _sanitize_prediction(float(interval.lower) if interval is not None else yhat, full_history, feature_spec=feature_spec)
                    upper = _sanitize_prediction(float(interval.upper) if interval is not None else yhat, full_history, feature_spec=feature_spec)
                    interval_bounds[level][0].append(lower)
                    interval_bounds[level][1].append(upper)
            full_history.append(yhat)
        forecast = pd.DataFrame({"ds": future_ds, "yhat": np.asarray(preds, dtype=float)})
        for level, (lowers, uppers) in interval_bounds.items():
            if lowers and uppers:
                forecast[f"lower_{level}"] = np.asarray(lowers, dtype=float)
                forecast[f"upper_{level}"] = np.asarray(uppers, dtype=float)
        return forecast

    if backend_id == "river_snarimax":
        regressor = preprocessing.StandardScaler() | linear_model.LinearRegression(optimizer=optim.Adam(0.001))
        model = time_series.SNARIMAX(
            p=min(5, max(2, season_length if season_length and season_length < 10 else 3)),
            d=1,
            q=1,
            m=season_length or 1,
            sp=1 if season_length and season_length > 1 else 0,
            sd=0,
            sq=0,
            regressor=regressor,
        )
        for ds_i, y_i, row in zip(ds, y, history.to_dict("records")):
            exog = _river_calendar_x(pd.Timestamp(ds_i))
            for col in exog_cols:
                exog[f"exog_{col}"] = float(row[col])
            model.learn_one(float(y_i), x=_sanitize_feature_dict(exog, feature_spec=feature_spec))
        xs = []
        for ds_i, exog in zip(future_ds, exog_future):
            x = _river_calendar_x(pd.Timestamp(ds_i))
            for col, value in exog.items():
                x[f"exog_{col}"] = value
            xs.append(_sanitize_feature_dict(x, feature_spec=feature_spec))
        preds = model.forecast(horizon, xs=xs)
        sanitized = [_sanitize_prediction(float(pred), y, feature_spec=feature_spec) for pred in preds]
        return pd.DataFrame({"ds": future_ds, "yhat": np.asarray(sanitized, dtype=float)})

    if backend_id == "river_holtwinters":
        gamma = 0.2 if season_length and season_length > 1 else None
        model = time_series.HoltWinters(alpha=0.35, beta=0.1, gamma=gamma, seasonality=season_length if season_length and season_length > 1 else 0)
        for y_i in y:
            model.learn_one(float(y_i))
        preds = model.forecast(horizon)
        sanitized = [_sanitize_prediction(float(pred), y, feature_spec=feature_spec) for pred in preds]
        return pd.DataFrame({"ds": future_ds, "yhat": np.asarray(sanitized, dtype=float)})

    raise AgentForecastError(code="UNSUPPORTED_RIVER_BACKEND", message=f"River backend '{backend_id}' is not supported.")


def _forecast_tabpfn(
    history: pd.DataFrame,
    future_features_df: pd.DataFrame,
    horizon: int,
    feature_spec: dict[str, Any],
) -> pd.DataFrame:
    from tabpfn import TabPFNRegressor

    X, y = build_supervised_matrix(history, feature_spec=feature_spec)
    X = _sanitize_feature_frame(X, feature_spec=feature_spec)
    model = TabPFNRegressor()
    model.fit(X, y)
    future_ds, step = _future_index(history, horizon)
    y_history = history["y"].astype(float).tolist()
    exog_cols = feature_spec.get("exogenous_cols", [])
    exog_future = future_exog_map(
        history,
        future_features_df,
        horizon=horizon,
        step=step,
        exogenous_cols=exog_cols,
        carry_forward=bool(feature_spec.get("carry_forward_exog", True)),
    )
    preds: list[float] = []
    for ds_i, exog in zip(future_ds, exog_future):
        feats = _sanitize_feature_dict(make_feature_row(pd.Timestamp(ds_i), y_history, feature_spec=feature_spec, exog_values=exog), feature_spec=feature_spec)
        x = _sanitize_feature_frame(pd.DataFrame([feats]).fillna(0.0), feature_spec=feature_spec)
        yhat = _sanitize_prediction(float(model.predict(x)[0]), y_history, feature_spec=feature_spec)
        preds.append(yhat)
        y_history.append(yhat)
    return pd.DataFrame({"ds": future_ds, "yhat": np.asarray(preds, dtype=float)})


def _forecast_direct_tabular(
    history: pd.DataFrame,
    future_features_df: pd.DataFrame,
    horizons: list[int],
    backend_id: str,
    feature_spec: dict[str, Any],
) -> pd.DataFrame:
    future_ds, step = _future_index(history, max(horizons))
    exog_cols = feature_spec.get("exogenous_cols", [])
    exog_future = future_exog_map(
        history,
        future_features_df,
        horizon=max(horizons),
        step=step,
        exogenous_cols=exog_cols,
        carry_forward=bool(feature_spec.get("carry_forward_exog", True)),
    )
    y_history = history["y"].astype(float).tolist()
    rows: list[dict[str, Any]] = []
    for horizon in horizons:
        X, y = build_supervised_matrix(history, feature_spec=feature_spec, target_horizon=horizon)
        X = _sanitize_feature_frame(X, feature_spec=feature_spec)
        model = _fit_sklearn_regression(backend_id)
        model.fit(X, y)
        feats = _sanitize_feature_dict(
            make_feature_row(
                pd.Timestamp(future_ds[horizon - 1]),
                y_history,
                feature_spec=feature_spec,
                exog_values=exog_future[horizon - 1],
            ),
            feature_spec=feature_spec,
        )
        x = _sanitize_feature_frame(pd.DataFrame([feats]).fillna(0.0), feature_spec=feature_spec)
        yhat = _sanitize_prediction(float(model.predict(x)[0]), y_history, feature_spec=feature_spec)
        rows.append({"ds": future_ds[horizon - 1], "horizon": int(horizon), "yhat": yhat, "mode": "direct"})
    return pd.DataFrame(rows)


def _forecast_direct_river_linear(
    history: pd.DataFrame,
    future_features_df: pd.DataFrame,
    horizons: list[int],
    feature_spec: dict[str, Any],
) -> pd.DataFrame:
    from river import linear_model, optim, preprocessing

    ds = pd.to_datetime(history["ds"]).tolist()
    y = history["y"].astype(float).tolist()
    future_ds, step = _future_index(history, max(horizons))
    exog_cols = feature_spec.get("exogenous_cols", [])
    exog_future = future_exog_map(
        history,
        future_features_df,
        horizon=max(horizons),
        step=step,
        exogenous_cols=exog_cols,
        carry_forward=bool(feature_spec.get("carry_forward_exog", True)),
    )
    history_records = history.to_dict("records")
    rows: list[dict[str, Any]] = []
    for horizon in horizons:
        X, target = build_supervised_matrix(history, feature_spec=feature_spec, target_horizon=horizon)
        model = preprocessing.StandardScaler() | linear_model.LinearRegression(optimizer=optim.Adam(0.001))
        for feat_row, target_value in zip(X.to_dict(orient="records"), target.tolist()):
            model.learn_one(_sanitize_feature_dict(feat_row, feature_spec=feature_spec), float(target_value))
        feats = _sanitize_feature_dict(
            make_feature_row(
                pd.Timestamp(future_ds[horizon - 1]),
                y,
                feature_spec=feature_spec,
                exog_values=exog_future[horizon - 1],
            ),
            feature_spec=feature_spec,
        )
        yhat = _sanitize_prediction(float(model.predict_one(feats) or _fallback_prediction(y)), y, feature_spec=feature_spec)
        rows.append({"ds": future_ds[horizon - 1], "horizon": int(horizon), "yhat": yhat, "mode": "direct"})
    return pd.DataFrame(rows)


def _forecast_direct_tabpfn(
    history: pd.DataFrame,
    future_features_df: pd.DataFrame,
    horizons: list[int],
    feature_spec: dict[str, Any],
) -> pd.DataFrame:
    from tabpfn import TabPFNRegressor

    future_ds, step = _future_index(history, max(horizons))
    exog_cols = feature_spec.get("exogenous_cols", [])
    exog_future = future_exog_map(
        history,
        future_features_df,
        horizon=max(horizons),
        step=step,
        exogenous_cols=exog_cols,
        carry_forward=bool(feature_spec.get("carry_forward_exog", True)),
    )
    y_history = history["y"].astype(float).tolist()
    rows: list[dict[str, Any]] = []
    for horizon in horizons:
        X, target = build_supervised_matrix(history, feature_spec=feature_spec, target_horizon=horizon)
        X = _sanitize_feature_frame(X, feature_spec=feature_spec)
        model = TabPFNRegressor()
        model.fit(X, target)
        feats = _sanitize_feature_dict(
            make_feature_row(
                pd.Timestamp(future_ds[horizon - 1]),
                y_history,
                feature_spec=feature_spec,
                exog_values=exog_future[horizon - 1],
            ),
            feature_spec=feature_spec,
        )
        x = _sanitize_feature_frame(pd.DataFrame([feats]).fillna(0.0), feature_spec=feature_spec)
        yhat = _sanitize_prediction(float(model.predict(x)[0]), y_history, feature_spec=feature_spec)
        rows.append({"ds": future_ds[horizon - 1], "horizon": int(horizon), "yhat": yhat, "mode": "direct"})
    return pd.DataFrame(rows)


def forecast_with_backend(
    history: pd.DataFrame,
    future_features_df: pd.DataFrame,
    *,
    horizon: int,
    backend_id: str,
    feature_spec: dict[str, Any],
    series_kind: str,
    conformal: ConformalSpec | None = None,
    carry_forward_exog: bool | None = None,
) -> pd.DataFrame:
    if carry_forward_exog is not None:
        feature_spec = {**feature_spec, "carry_forward_exog": bool(carry_forward_exog)}
    if not is_backend_available(backend_id):
        raise AgentForecastError(
            code="BACKEND_UNAVAILABLE",
            message=f"Backend '{backend_id}' is not installed.",
            help_text=f"Install the '{get_backend_spec(backend_id).extra}' extra or choose another backend.",
        )
    if backend_id in {"naive", "seasonal_naive", "moving_average", "drift"}:
        forecast = _forecast_baseline(history, horizon, backend_id)
    elif backend_id in {"stats_arima", "stats_ets"}:
        forecast = _forecast_stats(history, horizon, backend_id)
    elif backend_id in {"statsforecast_autoarima", "statsforecast_autoets"}:
        forecast = _forecast_statsforecast(history, horizon, backend_id)
    elif backend_id.startswith("ml_"):
        forecast = _forecast_tabular(history, future_features_df, horizon, backend_id, feature_spec)
    elif backend_id.startswith("mlforecast_"):
        forecast = _forecast_mlforecast(history, future_features_df, horizon, backend_id, feature_spec)
    elif backend_id.startswith("stream_"):
        forecast = _forecast_stream_builtin(history, future_features_df, horizon, backend_id, feature_spec)
    elif backend_id.startswith("river_"):
        forecast = _forecast_river(history, future_features_df, horizon, backend_id, feature_spec, conformal=conformal)
    elif backend_id == "tabpfn_regression":
        forecast = _forecast_tabpfn(history, future_features_df, horizon, feature_spec)
    else:
        raise AgentForecastError(
            code="BACKEND_ADAPTER_NOT_IMPLEMENTED",
            message=f"Backend '{backend_id}' is registered but no runtime adapter is implemented in this build.",
            help_text="This backend is intentionally optional and not shipped in the lean base path.",
        )
    if series_kind == "cumulative":
        for col in [item for item in forecast.columns if item.startswith(("yhat", "lower_", "upper_"))]:
            forecast[col] = np.maximum.accumulate(np.maximum(forecast[col].to_numpy(dtype=float), 0.0))
    return forecast


def forecast_horizons_with_backend(
    history: pd.DataFrame,
    future_features_df: pd.DataFrame,
    *,
    horizons: list[int] | tuple[int, ...],
    backend_id: str,
    feature_spec: dict[str, Any],
    series_kind: str,
    forecast_mode: str = "recursive",
    conformal: ConformalSpec | None = None,
    carry_forward_exog: bool | None = None,
) -> pd.DataFrame:
    resolved_horizons = _normalize_horizons(horizons)
    if forecast_mode == "recursive":
        forecast = forecast_with_backend(
            history,
            future_features_df,
            horizon=max(resolved_horizons),
            backend_id=backend_id,
            feature_spec=feature_spec,
            series_kind=series_kind,
            conformal=conformal,
            carry_forward_exog=carry_forward_exog,
        ).reset_index(drop=True)
        forecast = forecast.iloc[[horizon - 1 for horizon in resolved_horizons]].copy().reset_index(drop=True)
        forecast["horizon"] = resolved_horizons
        forecast["mode"] = "recursive"
        return forecast[["ds", "horizon", "yhat"] + [col for col in forecast.columns if col not in {"ds", "horizon", "yhat"}]]

    ensure(forecast_mode == "direct", "UNSUPPORTED_FORECAST_MODE", f"Unknown forecast mode '{forecast_mode}'.")
    if carry_forward_exog is not None:
        feature_spec = {**feature_spec, "carry_forward_exog": bool(carry_forward_exog)}
    ensure(
        supports_direct_forecast(backend_id),
        "DIRECT_MODE_UNSUPPORTED",
        f"Backend '{backend_id}' does not support direct multi-horizon forecasting.",
    )
    if backend_id.startswith("ml_"):
        forecast = _forecast_direct_tabular(history, future_features_df, resolved_horizons, backend_id, feature_spec)
    elif backend_id == "river_linear":
        forecast = _forecast_direct_river_linear(history, future_features_df, resolved_horizons, feature_spec)
    elif backend_id == "tabpfn_regression":
        forecast = _forecast_direct_tabpfn(history, future_features_df, resolved_horizons, feature_spec)
    else:
        raise AgentForecastError(code="DIRECT_MODE_UNSUPPORTED", message=f"Backend '{backend_id}' does not support direct multi-horizon forecasting.")
    if series_kind == "cumulative":
        forecast["yhat"] = np.maximum(forecast["yhat"].to_numpy(dtype=float), 0.0)
    return forecast


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    err = y_true - y_pred
    mae = float(np.mean(np.abs(err)))
    rmse = float(np.sqrt(np.mean(err ** 2)))
    denom = np.maximum(np.abs(y_true), 1e-8)
    mape = float(np.mean(np.abs(err) / denom) * 100.0)
    smape = float(np.mean(2.0 * np.abs(err) / np.maximum(np.abs(y_true) + np.abs(y_pred), 1e-8)) * 100.0)
    return {"mae": round(mae, 6), "rmse": round(rmse, 6), "mape": round(mape, 6), "smape": round(smape, 6)}


def _calibration_residuals(
    history: pd.DataFrame,
    future_features_df: pd.DataFrame,
    *,
    backend_id: str,
    horizon: int,
    feature_spec: dict[str, Any],
    series_kind: str,
) -> np.ndarray:
    max_lag = max(feature_spec.get("lags", [1]))
    min_train_size = max(max_lag + 2, 8)
    if len(history) <= min_train_size:
        return np.asarray([], dtype=float)

    calibration_horizon = min(max(3, horizon), max(3, len(history) // 5))
    calibration_horizon = min(calibration_horizon, len(history) - min_train_size)
    if calibration_horizon <= 0:
        return np.asarray([], dtype=float)

    calibration_train = history.iloc[:-calibration_horizon].reset_index(drop=True)
    calibration_test = history.iloc[-calibration_horizon:].reset_index(drop=True)
    try:
        calibration_pred = forecast_with_backend(
            calibration_train,
            pd.DataFrame(columns=future_features_df.columns),
            horizon=calibration_horizon,
            backend_id=backend_id,
            feature_spec=feature_spec,
            series_kind=series_kind,
            conformal=None,
        )
    except Exception:  # noqa: BLE001
        return np.asarray([], dtype=float)
    return calibration_test["y"].to_numpy(dtype=float) - calibration_pred["yhat"].to_numpy(dtype=float)


def _interval_metric_payload(y_true: np.ndarray, forecast: pd.DataFrame) -> dict[str, Any]:
    payload: dict[str, Any] = {"metrics": {}, "coverage": {}, "avg_width": {}, "wnc": {}}
    levels = sorted(
        {
            int(column.split("_", 1)[1])
            for column in forecast.columns
            if column.startswith("lower_") and f"upper_{column.split('_', 1)[1]}" in forecast.columns
        }
    )
    if not levels:
        return payload

    y_true = np.asarray(y_true, dtype=float)
    scale = max(float(np.mean(np.abs(y_true))), 1e-8)
    for level in levels:
        lower = forecast[f"lower_{level}"].to_numpy(dtype=float)
        upper = forecast[f"upper_{level}"].to_numpy(dtype=float)
        coverage = float(np.mean((y_true >= lower) & (y_true <= upper)))
        avg_width = float(np.mean(upper - lower))
        wnc = float(coverage / max(avg_width / scale, 1e-8))
        payload["metrics"][f"coverage_{level}"] = round(coverage, 6)
        payload["metrics"][f"avg_width_{level}"] = round(avg_width, 6)
        payload["metrics"][f"wnc_{level}"] = round(wnc, 6)
        payload["coverage"][str(level)] = round(coverage, 6)
        payload["avg_width"][str(level)] = round(avg_width, 6)
        payload["wnc"][str(level)] = round(wnc, 6)
    return payload


def score_backend(
    history: pd.DataFrame,
    future_features_df: pd.DataFrame,
    *,
    backend_id: str,
    horizon: int,
    feature_spec: dict[str, Any],
    series_kind: str,
    conformal: ConformalSpec | None = None,
) -> dict[str, Any]:
    if len(history) < 12:
        raise AgentForecastError(code="SERIES_TOO_SHORT", message="Need at least 12 points to compare backends robustly.")
    try:
        conformal_spec = resolve_conformal_spec(conformal, preserve_legacy_levels=conformal is None)
    except ValueError as exc:
        raise AgentForecastError(code="INVALID_CONFORMAL_SPEC", message=str(exc)) from exc
    back_h = min(max(3, horizon), max(3, len(history) // 5))
    train = history.iloc[:-back_h].reset_index(drop=True)
    test = history.iloc[-back_h:].reset_index(drop=True)
    calibration_residuals = _calibration_residuals(
        train,
        future_features_df,
        backend_id=backend_id,
        horizon=back_h,
        feature_spec=feature_spec,
        series_kind=series_kind,
    )
    test_pred = forecast_with_backend(
        train,
        pd.DataFrame(columns=future_features_df.columns),
        horizon=back_h,
        backend_id=backend_id,
        feature_spec=feature_spec,
        series_kind=series_kind,
        conformal=conformal_spec,
    )
    metrics = compute_metrics(test["y"].to_numpy(dtype=float), test_pred["yhat"].to_numpy(dtype=float))
    test_pred, test_conformal = _attach_intervals(
        test_pred,
        calibration_residuals,
        series_kind,
        backend_id=backend_id,
        conformal=conformal_spec,
    )
    residuals = test["y"].to_numpy(dtype=float) - test_pred["yhat"].to_numpy(dtype=float)
    interval_metrics = _interval_metric_payload(test["y"].to_numpy(dtype=float), test_pred)
    metrics.update(interval_metrics["metrics"])
    future_pred = forecast_with_backend(
        history,
        future_features_df,
        horizon=horizon,
        backend_id=backend_id,
        feature_spec=feature_spec,
        series_kind=series_kind,
        conformal=conformal_spec,
    )
    future_pred, future_conformal = _attach_intervals(
        future_pred,
        calibration_residuals,
        series_kind,
        backend_id=backend_id,
        conformal=conformal_spec,
    )
    conformal_payload = {
        **future_conformal,
        "coverage_backtest": interval_metrics["coverage"],
        "mean_interval_width": interval_metrics["avg_width"],
        "width_normalized_coverage": interval_metrics["wnc"],
        "calibration_size": int(calibration_residuals.size),
        "backend_tags": get_backend_spec(backend_id).tags,
    }
    if future_conformal["method"] != test_conformal["method"]:
        conformal_payload["backtest_method"] = test_conformal["method"]
    return {
        "backend_id": backend_id,
        "forecast": future_pred,
        "metrics": metrics,
        "residuals": residuals,
        "backtest_horizon": back_h,
        "backend_spec": get_backend_spec(backend_id).to_dict(),
        "conformal": conformal_payload,
    }
