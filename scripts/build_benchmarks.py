from __future__ import annotations

from pathlib import Path
import csv
import sys
import warnings

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import matplotlib.pyplot as plt
import pandas as pd

from agentforecast import compare_backends_dataset
from agentforecast.backends import is_backend_available
from agentforecast.benchmark_hub import list_external_benchmarks
from agentforecast.utils import ensure_dir

GEN = ensure_dir(ROOT / 'benchmarks' / 'generated')
RUNS = ensure_dir(ROOT / 'benchmarks' / 'runs')
DEMO_DATASETS = [
    'sales',
    'gold',
    'github-breakout',
    'air-quality-smoke',
    'icu-bed-stress',
    'beamline-drift',
    'transit-demand-shock',
]


def main() -> None:
    warnings.filterwarnings('ignore', category=UserWarning, module='statsmodels')
    backend_pool = [
        'naive',
        'seasonal_naive',
        'moving_average',
        'stream_ewm',
        'ml_ridge',
        'stats_arima',
        'stats_ets',
    ]
    backends = [backend_id for backend_id in backend_pool if is_backend_available(backend_id)]
    all_rows = []
    for dataset_id in DEMO_DATASETS:
        result = compare_backends_dataset(dataset_id, backends=backends, outdir=RUNS)
        leaderboard = pd.DataFrame(result.leaderboard).copy()
        leaderboard['dataset_id'] = dataset_id
        leaderboard['rank'] = range(1, len(leaderboard) + 1)
        all_rows.append(leaderboard)
    benchmark = pd.concat(all_rows, ignore_index=True)
    benchmark = benchmark[['dataset_id', 'backend_id', 'rank', 'mae', 'rmse', 'mape', 'smape', 'backtest_horizon']]
    benchmark.to_csv(GEN / 'transparent_public_benchmark.csv', index=False)

    rank_summary = benchmark.groupby('backend_id').agg(
        mean_rank=('rank', 'mean'),
        mean_mae=('mae', 'mean'),
        mean_rmse=('rmse', 'mean'),
        mean_smape=('smape', 'mean'),
        datasets=('dataset_id', 'nunique'),
    ).reset_index().sort_values(['mean_rank', 'mean_mae'])
    rank_summary.to_csv(GEN / 'backend_rank_summary.csv', index=False)

    rows = list_external_benchmarks()
    with (GEN / 'external_benchmark_links.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'kind', 'url', 'notes'])
        writer.writeheader()
        writer.writerows(rows)

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.bar(rank_summary['backend_id'], rank_summary['mean_rank'])
    ax.set_title('agentforecast internal demo benchmark: average rank across bundled demo datasets')
    ax.set_ylabel('mean rank (lower is better)')
    ax.set_xlabel('backend')
    ax.tick_params(axis='x', rotation=35)
    ax.grid(True, axis='y', alpha=0.25)
    fig.tight_layout()
    fig.savefig(GEN / 'transparent_public_benchmark.png', dpi=170)
    plt.close(fig)


if __name__ == '__main__':
    main()
