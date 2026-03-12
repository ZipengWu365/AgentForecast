from __future__ import annotations

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import matplotlib.image as mpimg
import matplotlib.pyplot as plt

from agentforecast.utils import ensure_dir

ASSETS = ensure_dir(ROOT / 'assets')
SITE = ROOT / 'public_gallery' / 'site'
_PREFERRED_KINDS = (
    'comparison_png',
    'forecast_card_png',
    'leaderboard_card_png',
    'delta_card_png',
    'drift_alert_card_png',
    'forecast_png',
)


def _pick(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(path)
    return path


def _preview_images(limit: int = 4) -> list[Path]:
    feed = json.loads((SITE / 'feed.json').read_text(encoding='utf-8'))
    images: list[Path] = []
    for item in feed.get('items', []):
        public_artifacts = item.get('public_artifacts', {})
        for kind in _PREFERRED_KINDS:
            raw = public_artifacts.get(kind)
            if not raw:
                continue
            candidate = _pick(SITE / raw)
            if candidate not in images:
                images.append(candidate)
                break
        if len(images) >= limit:
            break
    if not images:
        raise FileNotFoundError('No gallery preview images found in public_gallery/site/feed.json')
    return images


def main() -> None:
    images = _preview_images()
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
