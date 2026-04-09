# air_quality_smoke

- backend_selected: `moving_average`
- candidate_backends: `moving_average, stream_ewm, seasonal_naive, stats_arima, stats_ets, naive, ml_ridge`
- artifact_count: `11`
- requested_backend: `arena`
- resolved_backend: `moving_average`
- support_tier: `reviewed`
- latest_observed: `32.0800`
- projected_end: `40.5700`

Compared 7 backend(s) and routed the series to 'moving_average'. Exported CSV, chart, card, markdown, and JSON artifacts.

## Intervals

- enabled: `False`
- method: `residual_heuristic`
- levels: `80, 90`

## Leaderboard

| backend_id | mae | rmse | mape | smape | coverage_80 | avg_width_80 | wnc_80 | coverage_90 | avg_width_90 | wnc_90 | backtest_horizon |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| moving_average | 6.54939 | 8.00071 | 16.1425 | 16.1122 | 1 | 59.1936 | 0.685378 | 1 | 75.9735 | 0.534002 | 7 |
| stream_ewm | 7.17404 | 8.20962 | 19.0491 | 17.6015 | 1 | 58.3411 | 0.695393 | 1 | 74.8793 | 0.541805 | 7 |
| seasonal_naive | 13.1343 | 15.2656 | 34.7354 | 34.9253 | 1 | 85.9066 | 0.472257 | 1 | 110.259 | 0.367952 | 7 |
| stats_arima | 13.983 | 16.1026 | 39.6234 | 30.9668 | 1 | 59.1351 | 0.686056 | 1 | 75.8984 | 0.534531 | 7 |
| stats_ets | 14.055 | 16.6854 | 40.2738 | 30.9974 | 1 | 66.3412 | 0.611536 | 1 | 85.1472 | 0.476469 | 7 |
| naive | 14.81 | 16.8011 | 41.7187 | 32.4223 | 1 | 59.1936 | 0.685378 | 1 | 75.9735 | 0.534002 | 7 |
| ml_ridge | 17.5343 | 20.8727 | 50.3413 | 36.6179 | 1 | 58.4087 | 0.694588 | 1 | 74.966 | 0.541178 | 7 |

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
