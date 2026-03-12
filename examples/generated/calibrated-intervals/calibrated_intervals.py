from __future__ import annotations

from pathlib import Path
import pandas as pd
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agentforecast import ConformalSpec, forecast_dataframe
from agentforecast.backends import is_backend_available


def main() -> None:
    outdir = ROOT / "examples" / "generated" / "calibrated-intervals"
    df = pd.read_csv("https://raw.githubusercontent.com/jbrownlee/Datasets/master/airline-passengers.csv")
    backend = "river_linear" if is_backend_available("river_linear") else "stream_ewm"
    conformal = ConformalSpec(
        enabled=True,
        method="auto" if backend == "river_linear" else "rolling_residual",
        levels=(80, 90, 95),
        calibration_window=60,
        warmup_min=10,
    )
    result = forecast_dataframe(df, name="airline_passengers", backend=backend, outdir=outdir, horizon=12, conformal=conformal)
    print(result.summary["headline"])
    print((outdir / result.inputs["name"] / "data" / "forecast.csv").resolve())


if __name__ == "__main__":
    main()
