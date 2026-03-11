from __future__ import annotations

from dataclasses import asdict, dataclass
from statistics import NormalDist
from typing import Any, Callable
import math

import numpy as np
import pandas as pd


LEGACY_INTERVAL_LEVELS: tuple[int, ...] = (80, 90)
SUPPORTED_CONFORMAL_METHODS = {"auto", "river_jackknife", "rolling_residual"}


@dataclass
class ConformalSpec:
    enabled: bool = False
    method: str = "auto"
    levels: tuple[int, ...] = (80, 90, 95)
    calibration_window: int = 200
    warmup_min: int = 40
    symmetric: bool = True
    horizon_aware: bool = True

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["levels"] = list(self.levels)
        return payload


def resolve_conformal_spec(
    conformal: ConformalSpec | None,
    *,
    preserve_legacy_levels: bool = False,
) -> ConformalSpec:
    if conformal is None:
        levels = LEGACY_INTERVAL_LEVELS if preserve_legacy_levels else ConformalSpec().levels
        conformal = ConformalSpec(enabled=False, levels=levels)

    levels = tuple(sorted({int(level) for level in conformal.levels}))
    if not levels:
        raise ValueError("Conformal levels must not be empty.")
    if any(level <= 0 or level >= 100 for level in levels):
        raise ValueError("Conformal levels must be between 1 and 99.")
    if conformal.method not in SUPPORTED_CONFORMAL_METHODS:
        raise ValueError(f"Unsupported conformal method '{conformal.method}'.")
    if conformal.calibration_window <= 0:
        raise ValueError("Conformal calibration_window must be positive.")
    if conformal.warmup_min <= 0:
        raise ValueError("Conformal warmup_min must be positive.")

    return ConformalSpec(
        enabled=bool(conformal.enabled),
        method=conformal.method,
        levels=levels,
        calibration_window=int(conformal.calibration_window),
        warmup_min=int(conformal.warmup_min),
        symmetric=bool(conformal.symmetric),
        horizon_aware=bool(conformal.horizon_aware),
    )


def build_river_jackknife_wrappers(
    *,
    regressor_factory: Callable[[], Any],
    levels: tuple[int, ...],
    calibration_window: int,
) -> dict[int, Any]:
    from river import conf

    window_size = calibration_window or None
    return {
        level: conf.RegressionJackknife(
            regressor=regressor_factory(),
            confidence_level=level / 100.0,
            window_size=window_size,
        )
        for level in levels
    }


def attach_conformal_intervals(
    forecast: pd.DataFrame,
    *,
    spec: ConformalSpec | None,
    residuals: np.ndarray | None,
    series_kind: str,
    backend_id: str,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    effective_spec = resolve_conformal_spec(spec, preserve_legacy_levels=spec is None)
    forecast = forecast.copy()
    residuals = np.asarray(residuals if residuals is not None else [], dtype=float)
    requested_levels = effective_spec.levels
    existing_levels = tuple(_interval_levels(forecast))

    diagnostics: dict[str, Any] = {
        "enabled": effective_spec.enabled,
        "requested_method": effective_spec.method,
        "method": "residual_heuristic",
        "levels": list(requested_levels),
        "calibration_window": effective_spec.calibration_window,
        "warmup_min": effective_spec.warmup_min,
        "symmetric": effective_spec.symmetric,
        "horizon_aware": effective_spec.horizon_aware,
        "effective_horizon_aware": False,
        "calibration_size": int(residuals.size),
        "native_levels": list(existing_levels),
        "fallback_reason": None,
        "backend_id": backend_id,
    }

    if effective_spec.enabled and existing_levels and effective_spec.method in {"auto", "river_jackknife"}:
        diagnostics["method"] = "river_jackknife"
        if set(requested_levels).issubset(existing_levels):
            _apply_series_constraints(forecast, series_kind=series_kind)
            return forecast, diagnostics
        diagnostics["fallback_reason"] = "native_intervals_missing_requested_levels"
    elif effective_spec.enabled and effective_spec.method == "river_jackknife":
        diagnostics["fallback_reason"] = "backend_has_no_native_river_jackknife"

    if (
        effective_spec.enabled
        and effective_spec.method in {"auto", "rolling_residual"}
        and residuals.size >= effective_spec.warmup_min
    ):
        diagnostics["method"] = "rolling_residual"
        diagnostics["effective_horizon_aware"] = False
        _attach_residual_intervals(
            forecast,
            levels=requested_levels,
            residuals=residuals,
            symmetric=effective_spec.symmetric,
            calibration_window=effective_spec.calibration_window,
            overwrite=not bool(existing_levels),
        )
    else:
        if effective_spec.enabled and effective_spec.method == "rolling_residual" and residuals.size < effective_spec.warmup_min:
            diagnostics["fallback_reason"] = "insufficient_calibration_residuals"
        _attach_heuristic_intervals(
            forecast,
            levels=requested_levels,
            residuals=residuals,
            overwrite=not bool(existing_levels),
        )

    _apply_series_constraints(forecast, series_kind=series_kind)
    return forecast, diagnostics


def _interval_levels(forecast: pd.DataFrame) -> list[int]:
    levels = []
    for column in forecast.columns:
        if not column.startswith("lower_"):
            continue
        try:
            level = int(column.split("_", 1)[1])
        except ValueError:
            continue
        upper_col = f"upper_{level}"
        if upper_col in forecast.columns:
            levels.append(level)
    return sorted(set(levels))


def _apply_series_constraints(forecast: pd.DataFrame, *, series_kind: str) -> None:
    if series_kind != "cumulative":
        return
    for column in [item for item in forecast.columns if item.startswith(("yhat", "lower_", "upper_"))]:
        values = forecast[column].to_numpy(dtype=float)
        forecast[column] = np.maximum.accumulate(np.maximum(values, 0.0))


def _attach_heuristic_intervals(
    forecast: pd.DataFrame,
    *,
    levels: tuple[int, ...],
    residuals: np.ndarray,
    overwrite: bool,
) -> None:
    if residuals.size > 1:
        scale = float(np.std(residuals, ddof=1))
    elif residuals.size == 1:
        scale = float(np.abs(residuals).mean())
    elif len(forecast):
        scale = max(abs(float(forecast["yhat"].iloc[0])) * 0.05, 1.0)
    else:
        scale = 1.0
    scale = max(scale, 1.0)
    steps = np.sqrt(np.arange(1, len(forecast) + 1))
    for level in levels:
        lower_col = f"lower_{level}"
        upper_col = f"upper_{level}"
        if not overwrite and lower_col in forecast.columns and upper_col in forecast.columns:
            continue
        z_score = _normal_z(level / 100.0)
        width = z_score * scale * steps
        forecast[lower_col] = forecast["yhat"] - width
        forecast[upper_col] = forecast["yhat"] + width


def _attach_residual_intervals(
    forecast: pd.DataFrame,
    *,
    levels: tuple[int, ...],
    residuals: np.ndarray,
    symmetric: bool,
    calibration_window: int,
    overwrite: bool,
) -> None:
    window = residuals[-calibration_window:] if residuals.size > calibration_window else residuals
    for level in levels:
        lower_col = f"lower_{level}"
        upper_col = f"upper_{level}"
        if not overwrite and lower_col in forecast.columns and upper_col in forecast.columns:
            continue
        if symmetric:
            score = _conformal_abs_quantile(window, coverage=level / 100.0)
            forecast[lower_col] = forecast["yhat"] - score
            forecast[upper_col] = forecast["yhat"] + score
        else:
            lower_shift, upper_shift = _signed_residual_quantiles(window, coverage=level / 100.0)
            forecast[lower_col] = forecast["yhat"] + lower_shift
            forecast[upper_col] = forecast["yhat"] + upper_shift


def _conformal_abs_quantile(values: np.ndarray, *, coverage: float) -> float:
    if values.size == 0:
        return 0.0
    q = min(1.0, math.ceil((values.size + 1) * coverage) / values.size)
    return float(np.quantile(np.abs(values), q, method="higher"))


def _signed_residual_quantiles(values: np.ndarray, *, coverage: float) -> tuple[float, float]:
    if values.size == 0:
        return 0.0, 0.0
    alpha = (1.0 - coverage) / 2.0
    lower_q = float(np.quantile(values, alpha, method="lower"))
    upper_q = float(np.quantile(values, 1.0 - alpha, method="higher"))
    return lower_q, upper_q


def _normal_z(probability: float) -> float:
    z_lookup = {
        0.8: 1.2816,
        0.9: 1.6449,
        0.95: 1.96,
        0.99: 2.5758,
    }
    rounded = round(probability, 4)
    if rounded in z_lookup:
        return z_lookup[rounded]
    return float(NormalDist().inv_cdf((1.0 + probability) / 2.0))
