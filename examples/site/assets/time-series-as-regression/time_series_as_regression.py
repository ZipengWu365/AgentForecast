from __future__ import annotations

from pathlib import Path
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agentforecast import FeatureSpec, forecast_dataset


def main() -> None:
    outdir = ROOT / "examples" / "generated" / "time-series-as-regression"
    include_tsfresh = importlib.util.find_spec("tsfresh") is not None
    feature_spec = FeatureSpec(
        mode="tutorial_regression",
        lag_points=(1, 2, 3, 7, 14, 28),
        lag_step=7,
        lag_count=4,
        rolling_windows=(3, 7, 14, 28),
        include_tsfresh=include_tsfresh,
        tsfresh_window=28,
    )
    result = forecast_dataset("gold-exogenous", backend="ml_ridge", outdir=outdir, feature_spec=feature_spec)
    print(result.summary["headline"])
    print((outdir / "gold-exogenous" / "plots" / "forecast.png").resolve())


if __name__ == "__main__":
    main()
