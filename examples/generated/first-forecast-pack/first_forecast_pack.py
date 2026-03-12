from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agentforecast import forecast_dataset


def main() -> None:
    outdir = ROOT / "examples" / "generated" / "first-forecast-pack"
    result = forecast_dataset("sales", outdir=outdir, strategy="fast")
    print(result.summary["headline"])
    print((outdir / "sales" / "reports" / "summary.md").resolve())


if __name__ == "__main__":
    main()
