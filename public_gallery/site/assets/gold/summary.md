# gold

- backend_selected: `ml_ridge`
- candidate_backends: `ml_ridge, moving_average, naive, stats_arima`
- artifact_count: `10`
- latest_observed: `2623.5400`
- projected_end: `2705.8438`

Compared 4 backend(s) and routed the series to 'ml_ridge'. Exported CSV, chart, card, markdown, and JSON artifacts.

## Leaderboard

| backend_id | mae | rmse | mape | smape | backtest_horizon |
| --- | --- | --- | --- | --- | --- |
| ml_ridge | 9.80331 | 11.0612 | 0.374506 | 0.374609 | 30 |
| moving_average | 50.4416 | 54.2542 | 1.92179 | 1.94335 | 30 |
| naive | 66.083 | 69.0371 | 2.51954 | 2.55459 | 30 |
| stats_arima | 74.6889 | 77.686 | 2.84802 | 2.89249 | 30 |

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
