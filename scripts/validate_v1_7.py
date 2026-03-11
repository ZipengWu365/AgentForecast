from __future__ import annotations

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def require(path: str) -> None:
    p = ROOT / path
    if not p.exists():
        raise SystemExit(f'missing: {path}')


def main() -> None:
    required = [
        'README.md',
        'README.zh-CN.md',
        'LICENSE',
        'CONTRIBUTING.md',
        'CODE_OF_CONDUCT.md',
        'SECURITY.md',
        'CITATION.cff',
        'pyproject.toml',
        'agentforecast/backends.py',
        'agentforecast/hosted.py',
        'agentforecast/mcp_server.py',
        'agentforecast/package_data/manifests/mcp_manifest.json',
        'agentforecast/package_data/manifests/tool_manifest.json',
        'agentforecast/package_data/schemas/error.schema.json',
        'benchmarks/generated/transparent_public_benchmark.csv',
        'benchmarks/generated/backend_rank_summary.csv',
        'benchmarks/generated/external_benchmark_links.csv',
        'public_gallery/site/index.html',
        'public_gallery/site/feed.json',
        'assets/hosted_gallery_preview.png',
        'examples/notebooks/gold_price_with_exogenous_csv.ipynb',
        'examples/notebooks/choose_backend_by_strategy.ipynb',
        'examples/notebooks/when_ridge_beats_transformer.ipynb',
    ]
    for item in required:
        require(item)
    feed = json.loads((ROOT / 'public_gallery' / 'site' / 'feed.json').read_text(encoding='utf-8'))
    if not feed.get('items'):
        raise SystemExit('gallery feed has no items')
    print('validated v1.7 assets successfully')


if __name__ == '__main__':
    main()
