# gold

- backend_selected: `ml_ridge`
- candidate_backends: `ml_ridge, stats_ets, seasonal_naive, moving_average, naive, stats_arima, stream_ewm`
- artifact_count: `11`
- requested_backend: `arena`
- resolved_backend: `ml_ridge`
- support_tier: `reviewed`
- latest_observed: `2623.5400`
- projected_end: `2705.8438`

Compared 7 backend(s) and routed the series to 'ml_ridge'. Exported CSV, chart, card, markdown, and JSON artifacts.

## Intervals

- enabled: `False`
- method: `residual_heuristic`
- levels: `80, 90`

## Leaderboard

| backend_id | mae | rmse | mape | smape | coverage_80 | avg_width_80 | wnc_80 | coverage_90 | avg_width_90 | wnc_90 | backtest_horizon |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ml_ridge | 9.80331 | 11.0612 | 0.374506 | 0.374609 | 0.9 | 45.2717 | 52.0236 | 0.933333 | 58.105 | 42.0347 | 30 |
| stats_ets | 38.4194 | 40.2845 | 1.46562 | 1.47751 | 0.966667 | 142.754 | 17.7204 | 1 | 183.221 | 14.2827 | 30 |
| seasonal_naive | 50.1843 | 55.0462 | 1.91188 | 1.93405 | 0.966667 | 173.502 | 14.58 | 1 | 222.685 | 11.7515 | 30 |
| moving_average | 50.4416 | 54.2542 | 1.92179 | 1.94335 | 1 | 153.861 | 17.0081 | 1 | 197.476 | 13.2516 | 30 |
| naive | 66.083 | 69.0371 | 2.51954 | 2.55459 | 0.733333 | 153.861 | 12.4726 | 1 | 197.476 | 13.2516 | 30 |
| stats_arima | 74.6889 | 77.686 | 2.84802 | 2.89249 | 0.333333 | 135.389 | 6.44288 | 0.7 | 173.768 | 10.5417 | 30 |
| stream_ewm | 89.7567 | 96.9552 | 3.41984 | 3.48936 | 0.133333 | 137.261 | 2.54201 | 0.433333 | 176.171 | 6.43684 | 30 |

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
- `meta/artifact_manifest.json`
- `meta/metadata.json`
