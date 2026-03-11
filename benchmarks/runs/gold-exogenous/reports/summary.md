# gold_exogenous

- backend_selected: `ml_ridge`
- candidate_backends: `ml_ridge, naive, stats_arima, stats_ets, seasonal_naive, moving_average, stream_ewm`
- artifact_count: `10`
- latest_observed: `2108.4087`
- projected_end: `2118.0916`

Compared 7 backend(s) and routed the series to 'ml_ridge'. Exported CSV, chart, card, markdown, and JSON artifacts.

## Leaderboard

| backend_id | mae | rmse | mape | smape | backtest_horizon |
| --- | --- | --- | --- | --- | --- |
| ml_ridge | 3.75224 | 4.66322 | 0.179487 | 0.179316 | 30 |
| naive | 29.6768 | 35.31 | 1.4128 | 1.42699 | 30 |
| stats_arima | 31.2636 | 36.9216 | 1.48855 | 1.5041 | 30 |
| stats_ets | 32.2033 | 37.0174 | 1.5342 | 1.54985 | 30 |
| seasonal_naive | 35.5568 | 41.0811 | 1.69399 | 1.7133 | 30 |
| moving_average | 35.5673 | 40.9123 | 1.69443 | 1.71357 | 30 |
| stream_ewm | 43.6056 | 49.6992 | 2.07782 | 2.10615 | 30 |

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
