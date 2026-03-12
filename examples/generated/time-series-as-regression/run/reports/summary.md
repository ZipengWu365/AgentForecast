# gold_exogenous

- backend_selected: `ml_ridge`
- candidate_backends: `ml_ridge`
- artifact_count: `10`
- latest_observed: `2108.4087`
- projected_end: `2124.1734`

Compared 1 backend(s) and routed the series to 'ml_ridge'. Exported CSV, chart, card, markdown, and JSON artifacts.

## Intervals

- enabled: `False`
- method: `residual_heuristic`
- levels: `80, 90`

## Leaderboard

| backend_id | mae | rmse | mape | smape | coverage_80 | avg_width_80 | wnc_80 | coverage_90 | avg_width_90 | wnc_90 | backtest_horizon |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ml_ridge | 5.26426 | 6.5788 | 0.251421 | 0.251003 | 1 | 38.2021 | 54.6485 | 1 | 49.0314 | 42.5786 | 30 |

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
