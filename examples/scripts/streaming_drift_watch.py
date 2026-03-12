from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agentforecast import forecast_stream_csv
from agentforecast.backends import is_backend_available
from agentforecast.datasets import dataset_path


def main() -> None:
    outdir = ROOT / "examples" / "generated" / "streaming-drift-watch"
    backend = "river_snarimax" if is_backend_available("river_snarimax") else "stream_ewm"
    result = forecast_stream_csv(dataset_path("icu-bed-stress"), backend=backend, horizon=14, outdir=outdir)
    print(result.summary["headline"])
    print((outdir / "icu-bed-stress" / "plots" / "drift_alert_card.png").resolve())


if __name__ == "__main__":
    main()
