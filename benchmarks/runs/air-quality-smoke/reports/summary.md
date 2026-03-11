# air_quality_smoke

- backend_selected: `moving_average`
- candidate_backends: `moving_average, stream_ewm, seasonal_naive, stats_arima, stats_ets, naive, ml_ridge`
- artifact_count: `10`
- latest_observed: `32.0800`
- projected_end: `40.5700`

Compared 7 backend(s) and routed the series to 'moving_average'. Exported CSV, chart, card, markdown, and JSON artifacts.

## Leaderboard

| backend_id | mae | rmse | mape | smape | backtest_horizon |
| --- | --- | --- | --- | --- | --- |
| moving_average | 6.54939 | 8.00071 | 16.1425 | 16.1122 | 7 |
| stream_ewm | 7.17404 | 8.20962 | 19.0491 | 17.6015 | 7 |
| seasonal_naive | 13.1343 | 15.2656 | 34.7354 | 34.9253 | 7 |
| stats_arima | 13.983 | 16.1026 | 39.6234 | 30.9668 | 7 |
| stats_ets | 14.0562 | 16.6872 | 40.2774 | 30.9992 | 7 |
| naive | 14.81 | 16.8011 | 41.7187 | 32.4223 | 7 |
| ml_ridge | 17.5343 | 20.8727 | 50.3413 | 36.6179 | 7 |

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
