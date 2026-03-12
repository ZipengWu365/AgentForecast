from __future__ import annotations

from pathlib import Path
import pandas as pd
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agentforecast import compare_backends_frame
from agentforecast.backends import is_backend_available


def main() -> None:
    outdir = ROOT / "examples" / "generated" / "backend-arena"
    df = pd.read_csv("https://raw.githubusercontent.com/jbrownlee/Datasets/master/airline-passengers.csv")
    backends = [
        backend_id
        for backend_id in ["naive", "moving_average", "stats_arima", "stats_ets", "ml_ridge", "stream_ewm"]
        if is_backend_available(backend_id)
    ]
    result = compare_backends_frame(df, name="airline_passengers", backends=backends, outdir=outdir, horizon=12)
    print(result.summary["headline"])
    print((outdir / result.inputs["name"] / "data" / "leaderboard.csv").resolve())


if __name__ == "__main__":
    main()
