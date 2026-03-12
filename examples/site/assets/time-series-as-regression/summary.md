# daily_min_temperatures

- backend_selected: `ml_ridge`
- candidate_backends: `ml_ridge`
- artifact_count: `10`
- latest_observed: `13.0000`
- projected_end: `17.3298`

Compared 1 backend(s) and routed the series to 'ml_ridge'. Exported CSV, chart, card, markdown, and JSON artifacts.

## Intervals

- enabled: `False`
- method: `residual_heuristic`
- levels: `80, 90`

## Leaderboard

| backend_id | mae | rmse | mape | smape | coverage_80 | avg_width_80 | wnc_80 | coverage_90 | avg_width_90 | wnc_90 | backtest_horizon |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ml_ridge | 2.15176 | 2.79165 | 14.7479 | 14.605 | 1 | 27.4011 | 0.525648 | 1 | 35.1686 | 0.409551 | 30 |

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
