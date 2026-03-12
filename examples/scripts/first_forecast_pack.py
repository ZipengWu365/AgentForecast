from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agentforecast import forecast_csv
from agentforecast.public_examples import public_example_path


def main() -> None:
    outdir = ROOT / "examples" / "generated" / "first-forecast-pack"
    result = forecast_csv(public_example_path("monthly-car-sales"), outdir=outdir, horizon=12, strategy="fast")
    print(result.summary["headline"])
    print((outdir / "monthly-car-sales-real" / "reports" / "summary.md").resolve())


if __name__ == "__main__":
    main()
