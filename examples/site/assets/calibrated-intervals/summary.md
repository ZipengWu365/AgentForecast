# sales

- backend_selected: `river_linear`
- candidate_backends: `river_linear`
- artifact_count: `10`
- latest_observed: `164.0400`
- projected_end: `127.4961`

Compared 1 backend(s) and routed the series to 'river_linear'. Exported CSV, chart, card, markdown, and JSON artifacts.

## Intervals

- enabled: `True`
- method: `river_jackknife`
- levels: `80, 90, 95`

## Leaderboard

| backend_id | mae | rmse | mape | smape | coverage_80 | avg_width_80 | wnc_80 | coverage_90 | avg_width_90 | wnc_90 | coverage_95 | avg_width_95 | wnc_95 | backtest_horizon |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| river_linear | 45.0441 | 45.6519 | 27.6738 | 32.2043 | 0.714286 | 46.4723 | 2.48784 | 0.928571 | 60.0045 | 2.50482 | 1 | 67.2608 | 2.40648 | 14 |

## Artifacts
- `data/history.csv`
- `data/forecast.csv`
- `data/leaderboard.csv`
- `plots/forecast.png`
- `plots/forecast_card.png`
- `plots/backend_comparison.png`
- `plots/leaderboard_card.png`
- `plots/winner_vs_runnerup_delta.png`
- `reports/summary.md`
- `meta/metadata.json`
