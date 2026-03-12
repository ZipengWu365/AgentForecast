from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agentforecast import compare_backends_csv
from agentforecast.backends import is_backend_available
from agentforecast.public_examples import public_example_path


def main() -> None:
    outdir = ROOT / "examples" / "generated" / "backend-arena"
    backends = [
        backend_id
        for backend_id in ["naive", "moving_average", "stats_arima", "stats_ets", "ml_ridge", "stream_ewm"]
        if is_backend_available(backend_id)
    ]
    result = compare_backends_csv(public_example_path("airline-passengers"), backends=backends, outdir=outdir, horizon=12)
    print(result.summary["headline"])
    print((outdir / "airline-passengers-real" / "data" / "leaderboard.csv").resolve())


if __name__ == "__main__":
    main()
