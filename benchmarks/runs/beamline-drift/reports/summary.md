# beamline_drift

- backend_selected: `stats_arima`
- candidate_backends: `stats_arima, naive, stream_ewm, moving_average, seasonal_naive, stats_ets, ml_ridge`
- artifact_count: `11`
- requested_backend: `arena`
- resolved_backend: `stats_arima`
- support_tier: `reviewed`
- latest_observed: `3.2341`
- projected_end: `3.1342`

Compared 7 backend(s) and routed the series to 'stats_arima'. Exported CSV, chart, card, markdown, and JSON artifacts.

## Intervals

- enabled: `False`
- method: `residual_heuristic`
- levels: `80, 90`

## Leaderboard

| backend_id | mae | rmse | mape | smape | coverage_80 | avg_width_80 | wnc_80 | coverage_90 | avg_width_90 | wnc_90 | backtest_horizon |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| stats_arima | 0.142116 | 0.187135 | 4.68995 | 4.51298 | 1 | 6.70024 | 0.470955 | 1 | 8.59959 | 0.366938 | 14 |
| naive | 0.1444 | 0.189407 | 4.7655 | 4.58284 | 1 | 6.70024 | 0.470955 | 1 | 8.59959 | 0.366938 | 14 |
| stream_ewm | 0.14717 | 0.177237 | 4.60015 | 4.71763 | 1 | 6.70024 | 0.470955 | 1 | 8.59959 | 0.366938 | 14 |
| moving_average | 0.212416 | 0.259303 | 6.9837 | 6.62746 | 1 | 6.70024 | 0.470955 | 1 | 8.59959 | 0.366938 | 14 |
| seasonal_naive | 0.218771 | 0.280643 | 7.17567 | 6.77012 | 1 | 6.70024 | 0.470955 | 1 | 8.59959 | 0.366938 | 14 |
| stats_ets | 0.36611 | 0.429777 | 11.9309 | 11.0087 | 1 | 6.70024 | 0.470955 | 1 | 8.59959 | 0.366938 | 14 |
| ml_ridge | 0.691083 | 0.787224 | 21.9188 | 25.5761 | 1 | 6.70024 | 0.470955 | 1 | 8.59959 | 0.366938 | 14 |

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
