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
    strict_mode: bool


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


BENCHMARK_PRESETS: dict[str, dict[str, Any]] = {
    "benchmark_auto": {},
    "traffic_5min": {
        "lags": [1, 2, 3, 6, 12, 24, 36, 72, 144, 288],
        "rolling_windows": [12, 36, 72, 144],
        "include_calendar": False,
    },
    "eeg": {
        "lags": [1, 2, 4, 8, 16, 32, 64, 128],
        "rolling_windows": [4, 8, 16, 32],
        "include_calendar": False,
    },
    "daily_climate": {
        "lags": [1, 2, 3, 7, 14, 28, 56, 84],
        "rolling_windows": [3, 7, 14, 28],
        "include_calendar": False,
    },
    "flu": {
        "lags": [1, 2, 3, 4, 8, 12, 26, 52],
        "rolling_windows": [2, 4, 8, 12],
        "include_calendar": False,
    },
}


def list_feature_presets() -> list[dict[str, Any]]:
    return [
        {
            "preset": name,
            "lags": list(payload.get("lags", [])),
            "rolling_windows": list(payload.get("rolling_windows", [])),
            "include_calendar": bool(payload.get("include_calendar", False)),
        }
        for name, payload in sorted(BENCHMARK_PRESETS.items())
    ]


def _auto_benchmark_preset(history: pd.DataFrame, *, lookback: int | None = None) -> dict[str, Any]:
    ds = pd.to_datetime(history["ds"])
    freq_alias = infer_frequency_alias(ds)
    step = _infer_step(ds)
    if step <= pd.Timedelta(minutes=15):
        base = BENCHMARK_PRESETS["traffic_5min"]
    elif step <= pd.Timedelta(hours=1):
        base = {
            "lags": [1, 2, 3, 6, 12, 24, 48, 72, 96, 168],
            "rolling_windows": [6, 12, 24, 48],
            "include_calendar": False,
        }
    elif freq_alias and str(freq_alias).upper().startswith("W"):
        base = BENCHMARK_PRESETS["flu"]
    elif step <= pd.Timedelta(days=1):
        base = BENCHMARK_PRESETS["daily_climate"]
    else:
        base = {
            "lags": [1, 2, 3, 4, 8, 12],
            "rolling_windows": [2, 4, 8],
            "include_calendar": False,
        }
    payload = {
        "lags": list(base["lags"]),
        "rolling_windows": list(base["rolling_windows"]),
        "include_calendar": bool(base.get("include_calendar", False)),
    }
    if lookback is not None and lookback > 0:
        payload["lags"].append(int(lookback))
    return payload


def resolve_feature_preset(
    history: pd.DataFrame,
    *,
    feature_preset: str | None,
    lookback: int | None = None,
) -> dict[str, Any]:
    if feature_preset is None:
        return {}
    ensure(feature_preset in BENCHMARK_PRESETS, "UNKNOWN_FEATURE_PRESET", f"Unknown feature preset '{feature_preset}'.")
    if feature_preset == "benchmark_auto":
        return _auto_benchmark_preset(history, lookback=lookback)
    payload = dict(BENCHMARK_PRESETS[feature_preset])
    payload["lags"] = list(payload.get("lags", []))
    payload["rolling_windows"] = list(payload.get("rolling_windows", []))
    if lookback is not None and lookback > 0:
        payload.setdefault("lags", []).append(int(lookback))
    return payload


def infer_frequency_alias(ds: pd.Series) -> str | None:
    ordered = pd.Series(pd.to_datetime(ds, errors="coerce")).dropna().sort_values().drop_duplicates()
    if len(ordered) >= 3:
        try:
            inferred = pd.infer_freq(ordered)
        except ValueError:
            inferred = None
        if inferred:
            return str(inferred)
    step = _infer_step(ordered)
    if step == pd.Timedelta(hours=1):
        return "H"
    if step == pd.Timedelta(days=1):
        return "D"
    if step == pd.Timedelta(days=7):
        return "W"
    return None


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


def infer_season_length(step: pd.Timedelta, freq_alias: str | None = None) -> int | None:
    if freq_alias:
        normalized = str(freq_alias).upper()
        if normalized.startswith(("MS", "ME", "M")):
            return 12
        if normalized.startswith(("QS", "QE", "Q")):
            return 4
        if normalized.startswith("H"):
            return 24
        if normalized.startswith("D"):
            return 7
        if normalized.startswith("W"):
            return 4
    if step == pd.Timedelta(hours=1):
        return 24
    if step == pd.Timedelta(days=1):
        return 7
    if step == pd.Timedelta(days=7):
        return 4
    return None


def build_future_index(
    ds: pd.Series,
    horizon: int,
    *,
    freq_alias: str | None = None,
    step: pd.Timedelta | None = None,
) -> pd.DatetimeIndex:
    ordered = pd.Series(pd.to_datetime(ds, errors="coerce")).dropna().sort_values().drop_duplicates()
    if ordered.empty:
        return pd.DatetimeIndex([])
    resolved_freq = freq_alias or infer_frequency_alias(ordered)
    if resolved_freq:
        return pd.date_range(start=pd.Timestamp(ordered.iloc[-1]), periods=horizon + 1, freq=resolved_freq)[1:]
    resolved_step = step or _infer_step(ordered)
    return pd.date_range(start=pd.Timestamp(ordered.iloc[-1]) + resolved_step, periods=horizon, freq=resolved_step)


def infer_series_kind(values: pd.Series) -> str:
    arr = values.astype(float).to_numpy()
    if len(arr) >= 5 and np.all(arr >= 0):
        diffs = np.diff(arr)
        if len(diffs) and np.mean(diffs >= -1e-8) >= 0.92:
            return "cumulative"
    return "price"


def validate_series_frame(
    frame: pd.DataFrame,
    *,
    date_col: str = "ds",
    value_col: str = "y",
    strict_mode: bool = False,
) -> dict[str, Any]:
    issues: list[str] = []
    if date_col not in frame.columns:
        issues.append("missing_date_column")
    if value_col not in frame.columns:
        issues.append("missing_value_column")
    if issues:
        return {
            "ok": False,
            "strict_ready": False,
            "cleaning_recommended": False,
            "issues": issues,
        }

    work = frame.copy()
    work[date_col] = pd.to_datetime(work[date_col], errors="coerce")
    work[value_col] = pd.to_numeric(work[value_col], errors="coerce")
    history = work[work[value_col].notna()].copy()
    invalid_timestamps = int(work[date_col].isna().sum())
    invalid_values = int(history[value_col].isna().sum())
    duplicate_timestamps = int(history.duplicated(subset=[date_col]).sum()) if not history.empty else 0
    monotonic = bool(history[date_col].is_monotonic_increasing) if not history.empty else False
    inferred_frequency = infer_frequency_alias(history[date_col]) if len(history) >= 2 else None
    irregular_timestamps = 0
    if len(history) >= 3:
        if inferred_frequency:
            expected_index = pd.date_range(start=pd.Timestamp(history[date_col].iloc[0]), periods=len(history), freq=inferred_frequency)
            irregular_timestamps = int((pd.DatetimeIndex(history[date_col]) != expected_index).sum())
        else:
            step = _infer_step(history[date_col])
            irregular_timestamps = int((history[date_col].diff().dropna() != step).sum())

    strict_ready = (
        invalid_timestamps == 0
        and invalid_values == 0
        and duplicate_timestamps == 0
        and monotonic
        and irregular_timestamps == 0
        and len(history) >= 10
    )
    return {
        "ok": len(issues) == 0,
        "strict_mode": strict_mode,
        "strict_ready": strict_ready,
        "cleaning_recommended": bool(invalid_timestamps or duplicate_timestamps or irregular_timestamps),
        "issues": issues,
        "history_length": int(len(history)),
        "invalid_timestamps": invalid_timestamps,
        "invalid_values": invalid_values,
        "duplicate_timestamps": duplicate_timestamps,
        "is_monotonic": monotonic,
        "irregular_timestamps": irregular_timestamps,
        "inferred_frequency": inferred_frequency,
    }


def clean_series_frame(
    frame: pd.DataFrame,
    *,
    date_col: str = "ds",
    value_col: str = "y",
    series_kind: str = "auto",
    max_history: int | None = None,
) -> PreparedSeries:
    return prepare_series_frame(
        frame,
        date_col=date_col,
        value_col=value_col,
        series_kind=series_kind,
        strict_mode=False,
        max_history=max_history,
    )


def prepare_series_frame(
    frame: pd.DataFrame,
    *,
    date_col: str = "ds",
    value_col: str = "y",
    series_kind: str = "auto",
    strict_mode: bool = False,
    max_history: int | None = None,
) -> PreparedSeries:
    ensure(date_col in frame.columns, "DATE_COLUMN_NOT_FOUND", f"Column '{date_col}' was not found.")
    ensure(value_col in frame.columns, "VALUE_COLUMN_NOT_FOUND", f"Column '{value_col}' was not found.")
    if max_history is not None:
        max_history = int(max_history)
        ensure(max_history > 0, "INVALID_MAX_HISTORY", "max_history must be a positive integer when provided.")
    work = frame.copy()
    work[date_col] = pd.to_datetime(work[date_col], errors="coerce")
    work[value_col] = pd.to_numeric(work[value_col], errors="coerce")
    invalid_dates = int(work[date_col].isna().sum())
    if strict_mode:
        ensure(invalid_dates == 0, "STRICT_INVALID_DATES", "strict_mode does not allow invalid or missing timestamps.")
        work = work.reset_index(drop=True)
    else:
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
    if strict_mode:
        ensure(bool(history[date_col].is_monotonic_increasing), "STRICT_NON_MONOTONIC", "strict_mode requires timestamps to already be sorted in ascending order.")
        ensure(duplicate_count == 0, "STRICT_DUPLICATE_TIMESTAMPS", "strict_mode does not allow duplicate timestamps.")
        step = _infer_step(history[date_col])
        strict_freq_alias = infer_frequency_alias(history[date_col])
        if strict_freq_alias:
            expected_index = pd.date_range(
                start=pd.Timestamp(history[date_col].iloc[0]),
                periods=len(history),
                freq=strict_freq_alias,
            )
            irregular_count = int((pd.DatetimeIndex(history[date_col]) != expected_index).sum())
        else:
            diffs = history[date_col].diff().dropna()
            irregular_count = int((diffs != step).sum())
        ensure(irregular_count == 0, "STRICT_IRREGULAR_TIMESTEPS", "strict_mode does not allow implicit frequency repair or missing timestamp filling.")
        history = history.rename(columns={date_col: "ds", value_col: "y"}).reset_index(drop=True)
        missing_points = 0
        filled_history_values = 0
        filled_exog_values = 0
    else:
        agg_map = {value_col: "mean"}
        for col in extra_cols:
            agg_map[col] = "mean"
        history = history.groupby(date_col, as_index=False).agg(agg_map)

        step = _infer_step(history[date_col])
        freq_alias = infer_frequency_alias(history[date_col])
        inferred_frequency = freq_alias or _infer_frequency(step)
        full_index = pd.date_range(history[date_col].min(), history[date_col].max(), freq=freq_alias or step)
        reindexed = history.set_index(date_col).reindex(full_index)
        missing_points = int(reindexed[value_col].isna().sum())
        history_value_missing_before_fill = int(reindexed[value_col].isna().sum())
        exog_missing_before_fill = int(reindexed[extra_cols].isna().sum().sum()) if extra_cols else 0
        reindexed[value_col] = reindexed[value_col].interpolate(limit_direction="both").ffill().bfill()
        for col in extra_cols:
            reindexed[col] = reindexed[col].interpolate(limit_direction="both").ffill().bfill()
        history = reindexed.reset_index().rename(columns={"index": "ds", value_col: "y"})
        for col in extra_cols:
            history[col] = pd.to_numeric(history[col], errors="coerce").ffill().bfill()
        filled_history_values = history_value_missing_before_fill
        filled_exog_values = exog_missing_before_fill

    future = work[work[value_col].isna() & (work[date_col] > history["ds"].max())].copy()
    if not future.empty:
        if strict_mode:
            ensure(bool(future[date_col].is_monotonic_increasing), "STRICT_FUTURE_NON_MONOTONIC", "strict_mode requires future feature timestamps to already be sorted.")
        future = future[[date_col] + extra_cols].rename(columns={date_col: "ds"}).sort_values("ds").reset_index(drop=True)
    else:
        future = pd.DataFrame(columns=["ds"] + extra_cols)

    freq_alias = infer_frequency_alias(history["ds"])
    inferred_frequency = freq_alias or _infer_frequency(step)
    kind = infer_series_kind(history["y"]) if series_kind == "auto" else series_kind
    ensure(kind in {"price", "cumulative"}, "UNSUPPORTED_SERIES_KIND", f"Unknown series kind '{kind}'.")

    history_truncated = 0
    if max_history is not None and len(history) > max_history:
        history_truncated = int(len(history) - max_history)
        history = history.tail(max_history).reset_index(drop=True)

    cleanup = {
        "cleanup_applied": bool((missing_points or duplicate_count or history_truncated or filled_history_values or filled_exog_values) and not strict_mode),
        "missing_points_filled": missing_points,
        "duplicate_timestamps_merged": duplicate_count,
        "history_values_filled": filled_history_values,
        "exogenous_values_filled": filled_exog_values,
        "history_truncated": history_truncated,
        "history_rows_retained": int(len(history)),
        "inferred_frequency": inferred_frequency,
        "step_seconds": float(step.total_seconds()),
        "exogenous_cols": extra_cols,
        "future_feature_policy": "use_provided_only" if strict_mode else "use_provided_then_carry_last",
        "strict_mode": strict_mode,
        "invalid_timestamps_dropped": 0 if strict_mode else invalid_dates,
    }
    return PreparedSeries(
        history=history,
        future_features=future,
        cleanup=cleanup,
        inferred_frequency=inferred_frequency,
        step=step,
        series_kind=kind,
        exogenous_cols=extra_cols,
        strict_mode=strict_mode,
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
        return {"mode": features}
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
    feature_preset: str | None = None,
    lookback: int | None = None,
    benchmark_mode: bool = False,
) -> dict[str, Any]:
    n = len(history)
    if lookback is not None:
        lookback = int(lookback)
        ensure(lookback > 0, "INVALID_LOOKBACK", "lookback must be a positive integer when provided.")
    requested = _coerce_feature_spec(feature_spec, features=features)
    resolved_preset_name = requested.get("feature_preset") or requested.get("preset") or feature_preset
    if resolved_preset_name is None and benchmark_mode:
        resolved_preset_name = "benchmark_auto"
    preset_payload = resolve_feature_preset(history, feature_preset=resolved_preset_name, lookback=lookback) if resolved_preset_name else {}
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
        base_lags = list(preset_payload.get("lags", [1, 2, 3, 7, 14, 21, 28]))
        if lookback is not None:
            base_lags.append(int(lookback))
        lags = [lag for lag in sorted(set(base_lags)) if lag < n]
    if lookback is not None:
        lags = [lag for lag in lags if lag <= lookback]
    if not lags:
        lags = [lag for lag in [1, 2, 3] if lag < n]
    if not lags and n > 1:
        lags = [1]

    requested_rolling = _positive_int_list(requested.get("rolling_windows"))
    if requested_rolling:
        rolling_windows = [window for window in sorted(set(requested_rolling)) if window < n]
    else:
        rolling_base = list(preset_payload.get("rolling_windows", [3, 7, 14]))
        if lookback is not None:
            rolling_base = [window for window in rolling_base if window <= lookback]
        rolling_windows = [window for window in rolling_base if window < n]

    include_calendar_default = preset_payload.get("include_calendar", not benchmark_mode)
    include_calendar = bool(requested.get("include_calendar", include_calendar_default))
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
        "lookback": min(lookback, max(n - 1, 1)) if lookback is not None else None,
        "feature_preset": resolved_preset_name,
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
    target_horizon: int = 1,
) -> tuple[pd.DataFrame, pd.Series]:
    ensure(target_horizon > 0, "INVALID_TARGET_HORIZON", "target_horizon must be a positive integer.")
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

    max_target_idx = len(history) - target_horizon + 1
    for idx in range(max_lag, max_target_idx):
        target_idx = idx + target_horizon - 1
        feats = make_feature_row(
            ds_values[target_idx],
            y_values[:idx],
            feature_spec=feature_spec,
            exog_values=exog_maps[target_idx],
        )
        rows.append(feats)
        targets.append(float(y_values[target_idx]))
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
    carry_forward: bool = True,
) -> list[dict[str, float]]:
    if not exogenous_cols:
        return [{} for _ in range(horizon)]
    last_values = {col: float(history[col].iloc[-1]) for col in exogenous_cols} if carry_forward else {col: float("nan") for col in exogenous_cols}
    records = []
    future_by_ds = {}
    if not future_features.empty:
        temp = future_features.copy()
        temp["ds"] = pd.to_datetime(temp["ds"])
        for _, row in temp.iterrows():
            future_by_ds[pd.Timestamp(row["ds"])] = {col: float(row[col]) for col in exogenous_cols if col in row and pd.notna(row[col])}
    future_ds = build_future_index(history["ds"], horizon, step=step)
    for ds in future_ds:
        ds = pd.Timestamp(ds)
        values = dict(last_values)
        if ds in future_by_ds:
            values.update(future_by_ds[ds])
        if carry_forward:
            last_values = values
        records.append(values)
    return records
