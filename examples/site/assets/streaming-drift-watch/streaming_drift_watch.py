from __future__ import annotations

from pathlib import Path
import pandas as pd
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agentforecast import forecast_stream_dataframe
from agentforecast.backends import is_backend_available


def main() -> None:
    outdir = ROOT / "examples" / "generated" / "streaming-drift-watch"
    df = pd.read_csv("https://raw.githubusercontent.com/jbrownlee/Datasets/master/daily-min-temperatures.csv")
    backend = "river_snarimax" if is_backend_available("river_snarimax") else "stream_ewm"
    result = forecast_stream_dataframe(df, name="daily_min_temperatures", backend=backend, horizon=14, outdir=outdir)
    print(result.summary["headline"])
    print((outdir / result.inputs["name"] / "plots" / "drift_alert_card.png").resolve())


if __name__ == "__main__":
    main()
