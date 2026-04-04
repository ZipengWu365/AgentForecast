from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from .backends import resolve_backend_request, score_backend
from .conformal import ConformalSpec
from .features import FeatureSpec, build_feature_spec, prepare_series_frame
from .types import ResolutionInfo


@dataclass
class OnlineForecaster:
    backend: str = "auto"
    strategy: str = "fast"
    strict_backend: bool = True
    allow_backend_substitution: bool = False
    mode: str = "research"
    resolution: ResolutionInfo | None = None

    def resolve(
        self,
        frame: pd.DataFrame,
        *,
        date_col: str = "ds",
        value_col: str = "y",
        horizon: int = 30,
        series_kind: str = "auto",
    ) -> ResolutionInfo:
        prepared = prepare_series_frame(frame, date_col=date_col, value_col=value_col, series_kind=series_kind)
        resolution = resolve_backend_request(
            self.backend,
            history_len=len(prepared.history),
            horizon=horizon,
            strategy=self.strategy,
            exogenous_cols=prepared.exogenous_cols,
            mode=self.mode,
            strict_backend=self.strict_backend,
            allow_backend_substitution=self.allow_backend_substitution,
        )
        self.resolution = resolution
        return resolution

    def backtest(
        self,
        frame: pd.DataFrame,
        *,
        date_col: str = "ds",
        value_col: str = "y",
        horizon: int = 30,
        series_kind: str = "auto",
        conformal: ConformalSpec | None = None,
        feature_spec: FeatureSpec | dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        prepared = prepare_series_frame(frame, date_col=date_col, value_col=value_col, series_kind=series_kind)
        built_feature_spec = build_feature_spec(prepared.history, feature_spec=feature_spec)
        resolution = self.resolve(
            frame,
            date_col=date_col,
            value_col=value_col,
            horizon=horizon,
            series_kind=series_kind,
        )
        scored = score_backend(
            prepared.history,
            prepared.future_features,
            backend_id=resolution.resolved_backend,
            horizon=horizon,
            feature_spec=built_feature_spec,
            series_kind=prepared.series_kind,
            conformal=conformal,
        )
        return {
            "kind": "agentforecast.online_forecaster_result",
            "backend_selected": resolution.resolved_backend,
            "requested_backend": resolution.requested_backend,
            "strict_backend": self.strict_backend,
            "allow_backend_substitution": self.allow_backend_substitution,
            "resolution": resolution.to_dict(),
            "feature_spec": built_feature_spec,
            "metrics": scored["metrics"],
            "backtest_horizon": scored["backtest_horizon"],
            "conformal": scored["conformal"],
            "backend_spec": scored["backend_spec"],
            "forecast": scored["forecast"].to_dict(orient="records"),
        }
