from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agentforecast.cli import _demo_gallery


def main() -> None:
    _demo_gallery(str(ROOT / 'public_gallery' / 'demo_runs'), str(ROOT / 'public_gallery' / 'site'))


if __name__ == '__main__':
    main()
