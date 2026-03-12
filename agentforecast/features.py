from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
import importlib.util
import math
import warnings

import numpy as np
import pandas as pd

from .errors import ensure

DEFAULT_CALENDAR_FEATURES = (
    "dayofweek",
    "month",
    "day",
    "dayofyear",
    "is_month_start",
    "is_month_end",
    "ordinal",
    "sin_dayofyear",
    "cos_dayofyear",
)
DEFAULT_TSFRESH_FEATURES = (
    "absolute_sum_of_changes",
    "autocorrelation_lag_1",
    "autocorrelation_lag_7",
    "cid_ce",
    "count_above_mean",
    "longest_strike_above_mean",
    "number_peaks_3",
    "sample_entropy",
)


@dataclass
class PreparedSeries:
    history: pd.DataFrame
    future_features: pd.DataFrame
    cleanup: dict[str, Any]
    inferred_frequency: str
    step: pd.Timedelta
    series_kind: str
    exogenous_cols: list[str]


@dataclass
class FeatureSpec:
    mode: str = "auto"
    lag_points: tuple[int, ...] | None = None
    lag_step: int | None = None
    lag_count: int | None = None
    rolling_windows: tuple[int, ...] | None = None
    include_calendar: bool = True
    calendar_features: tuple[str, ...] = field(default_factory=lambda: DEFAULT_CALENDAR_FEATURES)
    include_tsfresh: bool = False
    tsfresh_window: int = 30
    tsfresh_features: tuple[str, ...] = field(default_factory=lambda: DEFAULT_TSFRESH_FEATURES)
    include_exogenous: bool = True

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        for key in ("lag_points", "rolling_windows", "calendar_features", "tsfresh_features"):
            if payload[key] is not None:
                payload[key] = list(payload[key])
        return payload


def _infer_step(ds: pd.Series) -> pd.Timedelta:
    diffs = ds.sort_values().diff().dropna()
    if diffs.empty:
        return pd.Timedelta(days=1)
    mode = diffs.mode()
    if len(mode) > 0:
        return mode.iloc[0]
    return diffs.iloc[0]


def _infer_frequency(step: pd.Timedelta) -> str:
    day = pd.Timedelta(days=1)
    hour = pd.Timedelta(hours=1)
    week = pd.Timedelta(days=7)
    if step == hour:
        return "H"
    if step == day:
        return "D"
    if step == week:
        return "W"
    return "custom"


def infer_season_length(step: pd.Timedelta) -> int | None:
    if step == pd.Timedelta(hours=1):
        return 24
    if step == pd.Timedelta(days=1):
        return 7
    if step == pd.Timedelta(days=7):
        return 4
    return None


def infer_series_kind(values: pd.Series) -> str:
    arr = values.astype(float).to_numpy()
    if len(arr) >= 5 and np.all(arr >= 0):
        diffs = np.diff(arr)
        if len(diffs) and np.mean(diffs >= -1e-8) >= 0.92:
            return "cumulative"
    return "price"


def prepare_series_frame(frame: pd.DataFrame, *, date_col: str = "ds", value_col: str = "y", series_kind: str = "auto") -> PreparedSeries:
    ensure(date_col in frame.columns, "DATE_COLUMN_NOT_FOUND", f"Column '{date_col}' was not found.")
    ensure(value_col in frame.columns, "VALUE_COLUMN_NOT_FOUND", f"Column '{value_col}' was not found.")
    work = frame.copy()
    work[date_col] = pd.to_datetime(work[date_col], errors="coerce")
    work[value_col] = pd.to_numeric(work[value_col], errors="coerce")
    work = work.dropna(subset=[date_col]).sort_values(date_col).reset_index(drop=True)

    extra_cols: list[str] = []
    for col in work.columns:
        if col in (date_col, value_col):
            continue
        work[col] = pd.to_numeric(work[col], errors="coerce")
        if not work[col].isna().all():
            extra_cols.append(col)

    history = work[work[value_col].notna()].copy()
    ensure(len(history) >= 10, "SERIES_TOO_SHORT", "Need at least 10 non-null observations to forecast.")
    duplicate_count = int(history.duplicated(subset=[date_col]).sum())
    agg_map = {value_col: "mean"}
    for col in extra_cols:
        agg_map[col] = "mean"
    history = history.groupby(date_col, as_index=False).agg(agg_map)

    step = _infer_step(history[date_col])
    inferred_frequency = _infer_frequency(step)
    full_index = pd.date_range(history[date_col].min(), history[date_col].max(), freq=step)
    reindexed = history.set_index(date_col).reindex(full_index)
    missing_points = int(reindexed[value_col].isna().sum())
    reindexed[value_col] = reindexed[value_col].interpolate(limit_direction="both").ffill().bfill()
    for col in extra_cols:
        reindexed[col] = reindexed[col].interpolate(limit_direction="both").ffill().bfill()
    history = reindexed.reset_index().rename(columns={"index": "ds", value_col: "y"})
    for col in extra_cols:
        history[col] = pd.to_numeric(history[col], errors="coerce").ffill().bfill()

    future = work[work[value_col].isna() & (work[date_col] > history["ds"].max())].copy()
    if not future.empty:
        future = future[[date_col] + extra_cols].rename(columns={date_col: "ds"}).sort_values("ds").reset_index(drop=True)
    else:
        future = pd.DataFrame(columns=["ds"] + extra_cols)

    kind = infer_series_kind(history["y"]) if series_kind == "auto" else series_kind
    ensure(kind in {"price", "cumulative"}, "UNSUPPORTED_SERIES_KIND", f"Unknown series kind '{kind}'.")

    cleanup = {
        "cleanup_applied": bool(missing_points or duplicate_count),
        "missing_points_filled": missing_points,
        "duplicate_timestamps_merged": duplicate_count,
        "inferred_frequency": inferred_frequency,
        "step_seconds": float(step.total_seconds()),
        "exogenous_cols": extra_cols,
        "future_feature_policy": "use_provided_then_carry_last",
    }
    return PreparedSeries(
        history=history,
        future_features=future,
        cleanup=cleanup,
        inferred_frequency=inferred_frequency,
        step=step,
        series_kind=kind,
        exogenous_cols=extra_cols,
    )


def _positive_int_list(values: Any) -> list[int]:
    if values is None:
        return []
    if isinstance(values, str):
        values = [item.strip() for item in values.split(",") if item.strip()]
    normalized: list[int] = []
    for value in values:
        item = int(value)
        ensure(item > 0, "INVALID_FEATURE_SPEC", "Lag, delay, and rolling values must be positive integers.")
        normalized.append(item)
    return normalized


def _has_tsfresh() -> bool:
    return importlib.util.find_spec("tsfresh") is not None


def _coerce_feature_spec(feature_spec: FeatureSpec | dict[str, Any] | None, *, features: str) -> dict[str, Any]:
    if feature_spec is None:
        return FeatureSpec(mode=features).to_dict()
    if isinstance(feature_spec, FeatureSpec):
        payload = feature_spec.to_dict()
    else:
        payload = dict(feature_spec)
    payload.setdefault("mode", features)
    return payload


def build_feature_spec(
    history: pd.DataFrame,
    *,
    features: str = "auto",
    feature_spec: FeatureSpec | dict[str, Any] | None = None,
) -> dict[str, Any]:
    n = len(history)
    requested = _coerce_feature_spec(feature_spec, features=features)
    explicit_lags = _positive_int_list(requested.get("lags", requested.get("lag_points")))
    lag_step = requested.get("lag_step")
    lag_count = requested.get("lag_count")
    if lag_step is not None:
        lag_step = int(lag_step)
        ensure(lag_step > 0, "INVALID_FEATURE_SPEC", "lag_step must be positive when provided.")
    if lag_count is not None:
        lag_count = int(lag_count)
        ensure(lag_count > 0, "INVALID_FEATURE_SPEC", "lag_count must be positive when provided.")

    if explicit_lags or (lag_step and lag_count):
        lag_candidates = set(explicit_lags)
        if lag_step and lag_count:
            lag_candidates.update(lag_step * idx for idx in range(1, lag_count + 1))
        lags = sorted(lag for lag in lag_candidates if lag < n)
    else:
        base_lags = [1, 2, 3, 7, 14, 21, 28]
        lags = [lag for lag in base_lags if lag < n]
    if not lags:
        lags = [lag for lag in [1, 2, 3] if lag < n]
    if not lags and n > 1:
        lags = [1]

    requested_rolling = _positive_int_list(requested.get("rolling_windows"))
    if requested_rolling:
        rolling_windows = [window for window in sorted(set(requested_rolling)) if window < n]
    else:
        rolling_windows = [window for window in [3, 7, 14] if window < n]

    include_calendar = bool(requested.get("include_calendar", True))
    calendar_features = tuple(DEFAULT_CALENDAR_FEATURES)
    if include_calendar:
        requested_calendar = requested.get("calendar_features")
        if requested_calendar is not None:
            calendar_features = tuple(str(item) for item in requested_calendar)
    else:
        calendar_features = ()

    include_tsfresh = bool(requested.get("include_tsfresh", requested.get("tsfresh", False)))
    tsfresh_window = int(requested.get("tsfresh_window", 30))
    ensure(tsfresh_window > 1, "INVALID_FEATURE_SPEC", "tsfresh_window must be greater than 1.")
    tsfresh_features = tuple(str(item) for item in requested.get("tsfresh_features", DEFAULT_TSFRESH_FEATURES))
    if include_tsfresh:
        ensure(
            _has_tsfresh(),
            "TSFRESH_NOT_INSTALLED",
            "tsfresh features were requested but the tsfresh package is not installed.",
            help_text='Install the optional feature stack with `pip install "agentforecast[features]"`.',
        )

    include_exogenous = bool(requested.get("include_exogenous", True))
    exogenous_cols = [col for col in history.columns if col not in {"ds", "y"}] if include_exogenous else []
    return {
        "mode": requested.get("mode", features),
        "lags": lags,
        "lag_points": explicit_lags,
        "lag_step": lag_step,
        "lag_count": lag_count,
        "rolling_windows": rolling_windows,
        "include_calendar": include_calendar,
        "calendar_features": list(calendar_features),
        "include_tsfresh": include_tsfresh,
        "tsfresh_window": tsfresh_window,
        "tsfresh_features": list(tsfresh_features if include_tsfresh else []),
        "include_exogenous": include_exogenous,
        "exogenous_cols": exogenous_cols,
    }


def _calendar_feature_map(ds: pd.Timestamp) -> dict[str, float]:
    return {
        "dayofweek": float(ds.dayofweek),
        "month": float(ds.month),
        "day": float(ds.day),
        "dayofyear": float(ds.dayofyear),
        "is_month_start": float(ds.is_month_start),
        "is_month_end": float(ds.is_month_end),
        "ordinal": float(ds.toordinal()),
        "sin_dayofyear": math.sin(2 * math.pi * ds.dayofyear / 365.25),
        "cos_dayofyear": math.cos(2 * math.pi * ds.dayofyear / 365.25),
    }


def _tsfresh_feature_map(y_history: list[float], *, feature_spec: dict[str, Any]) -> dict[str, float]:
    if not feature_spec.get("include_tsfresh"):
        return {}
    from tsfresh.feature_extraction import feature_calculators as fc

    window = min(int(feature_spec.get("tsfresh_window", 30)), len(y_history))
    series = np.asarray(y_history[-window:], dtype=float)
    feature_names = feature_spec.get("tsfresh_features", [])
    if series.size < 3:
        return {f"tsfresh_{name}": 0.0 for name in feature_names}

    calculators: dict[str, Any] = {
        "absolute_sum_of_changes": lambda values: fc.absolute_sum_of_changes(values),
        "autocorrelation_lag_1": lambda values: fc.autocorrelation(values, lag=min(1, max(len(values) - 1, 1))),
        "autocorrelation_lag_7": lambda values: fc.autocorrelation(values, lag=min(7, max(len(values) - 1, 1))),
        "cid_ce": lambda values: fc.cid_ce(values, normalize=True),
        "count_above_mean": lambda values: fc.count_above_mean(values),
        "longest_strike_above_mean": lambda values: fc.longest_strike_above_mean(values),
        "number_peaks_3": lambda values: fc.number_peaks(values, n=3),
        "sample_entropy": lambda values: fc.sample_entropy(values),
    }
    features: dict[str, float] = {}
    for name in feature_names:
        calculator = calculators.get(name)
        if calculator is None:
            features[f"tsfresh_{name}"] = 0.0
            continue
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                with np.errstate(all="ignore"):
                    value = float(calculator(series))
        except Exception:  # noqa: BLE001
            value = 0.0
        if not np.isfinite(value):
            value = 0.0
        features[f"tsfresh_{name}"] = value
    return features


def make_feature_row(
    ds: pd.Timestamp,
    y_history: list[float],
    *,
    feature_spec: dict[str, Any],
    exog_values: dict[str, float] | None = None,
) -> dict[str, float]:
    feats: dict[str, float] = {}
    lags = feature_spec.get("lags", [])
    for lag in lags:
        feats[f"lag_{lag}"] = float(y_history[-lag])
    for window in feature_spec.get("rolling_windows", []):
        recent = np.asarray(y_history[-window:], dtype=float)
        feats[f"roll_mean_{window}"] = float(recent.mean())
        feats[f"roll_std_{window}"] = float(recent.std(ddof=0))
        feats[f"roll_min_{window}"] = float(recent.min())
        feats[f"roll_max_{window}"] = float(recent.max())
    if feature_spec.get("include_calendar", True):
        calendar_map = _calendar_feature_map(ds)
        for key in feature_spec.get("calendar_features", []):
            if key in calendar_map:
                feats[key] = float(calendar_map[key])
    feats.update(_tsfresh_feature_map(y_history, feature_spec=feature_spec))
    feats["history_len"] = float(len(y_history))
    if exog_values:
        for key, value in exog_values.items():
            feats[f"exog_{key}"] = float(value)
    return feats


def build_supervised_matrix(
    history: pd.DataFrame,
    *,
    feature_spec: dict[str, Any],
) -> tuple[pd.DataFrame, pd.Series]:
    lags = feature_spec.get("lags", [])
    max_lag = max(lags) if lags else 1
    rows: list[dict[str, float]] = []
    targets: list[float] = []
    exog_cols = feature_spec.get("exogenous_cols", [])
    y_values = history["y"].astype(float).tolist()
    ds_values = list(pd.to_datetime(history["ds"]))
    exog_maps = []
    if exog_cols:
        for _, row in history[exog_cols].iterrows():
            exog_maps.append({col: float(row[col]) for col in exog_cols})
    else:
        exog_maps = [{} for _ in range(len(history))]

    for idx in range(max_lag, len(history)):
        feats = make_feature_row(
            ds_values[idx],
            y_values[:idx],
            feature_spec=feature_spec,
            exog_values=exog_maps[idx],
        )
        rows.append(feats)
        targets.append(float(y_values[idx]))
    ensure(len(rows) >= 5, "SUPERVISED_FRAME_TOO_SMALL", "Not enough rows after lag construction to fit a regression backend.")
    X = pd.DataFrame(rows).fillna(0.0)
    y = pd.Series(targets)
    return X, y


def future_exog_map(
    history: pd.DataFrame,
    future_features: pd.DataFrame,
    *,
    horizon: int,
    step: pd.Timedelta,
    exogenous_cols: list[str],
) -> list[dict[str, float]]:
    if not exogenous_cols:
        return [{} for _ in range(horizon)]
    last_ds = pd.to_datetime(history["ds"].iloc[-1])
    last_values = {col: float(history[col].iloc[-1]) for col in exogenous_cols}
    records = []
    future_by_ds = {}
    if not future_features.empty:
        temp = future_features.copy()
        temp["ds"] = pd.to_datetime(temp["ds"])
        for _, row in temp.iterrows():
            future_by_ds[pd.Timestamp(row["ds"])] = {col: float(row[col]) for col in exogenous_cols if col in row and pd.notna(row[col])}
    for i in range(1, horizon + 1):
        ds = pd.Timestamp(last_ds + i * step)
        values = dict(last_values)
        if ds in future_by_ds:
            values.update(future_by_ds[ds])
        last_values = values
        records.append(values)
    return records
