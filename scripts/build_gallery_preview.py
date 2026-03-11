from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import matplotlib.image as mpimg
import matplotlib.pyplot as plt

from agentforecast.utils import ensure_dir

ASSETS = ensure_dir(ROOT / 'assets')
SITE = ROOT / 'public_gallery' / 'site' / 'assets'


def _pick(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(path)
    return path


def main() -> None:
    images = [
        _pick(SITE / 'sales' / 'forecast_card.png'),
        _pick(SITE / 'gold' / 'leaderboard_card.png'),
        _pick(SITE / 'github-breakout' / 'forecast_card.png'),
        _pick(SITE / 'gold' / 'winner_vs_runnerup_delta.png'),
    ]
    fig = plt.figure(figsize=(12, 8))
    gs = fig.add_gridspec(2, 2)
    for idx, path in enumerate(images):
        ax = fig.add_subplot(gs[idx // 2, idx % 2])
        ax.imshow(mpimg.imread(path))
        ax.set_title(path.parent.name.replace('-', ' '))
        ax.axis('off')
    fig.suptitle('agentforecast hosted gallery preview', fontsize=16)
    fig.tight_layout()
    fig.savefig(ASSETS / 'hosted_gallery_preview.png', dpi=180)
    plt.close(fig)


if __name__ == '__main__':
    main()
