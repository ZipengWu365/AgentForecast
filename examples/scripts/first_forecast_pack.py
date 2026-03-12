from __future__ import annotations

from pathlib import Path
import pandas as pd
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agentforecast import forecast_dataframe


def main() -> None:
    outdir = ROOT / "examples" / "generated" / "first-forecast-pack"
    df = pd.read_csv("https://raw.githubusercontent.com/jbrownlee/Datasets/master/monthly-car-sales.csv")
    result = forecast_dataframe(df, name="monthly_car_sales", outdir=outdir, horizon=12, strategy="fast")
    print(result.summary["headline"])
    print((outdir / result.inputs["name"] / "reports" / "summary.md").resolve())


if __name__ == "__main__":
    main()
