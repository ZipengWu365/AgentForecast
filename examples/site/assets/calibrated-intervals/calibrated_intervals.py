from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agentforecast import ConformalSpec, forecast_csv
from agentforecast.backends import is_backend_available
from agentforecast.public_examples import public_example_path


def main() -> None:
    outdir = ROOT / "examples" / "generated" / "calibrated-intervals"
    backend = "river_linear" if is_backend_available("river_linear") else "stream_ewm"
    conformal = ConformalSpec(
        enabled=True,
        method="auto" if backend == "river_linear" else "rolling_residual",
        levels=(80, 90, 95),
        calibration_window=60,
        warmup_min=10,
    )
    result = forecast_csv(public_example_path("airline-passengers"), backend=backend, outdir=outdir, horizon=12, conformal=conformal)
    print(result.summary["headline"])
    print((outdir / "airline-passengers-real" / "data" / "forecast.csv").resolve())


if __name__ == "__main__":
    main()
