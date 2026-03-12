from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agentforecast.examples_hub import demo_examples


def main() -> None:
    demo_examples(ROOT / "examples" / "generated", ROOT / "examples" / "site")


if __name__ == "__main__":
    main()
