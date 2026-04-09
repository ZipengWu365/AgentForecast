# transit_demand_shock

- backend_selected: `stats_ets`
- candidate_backends: `stats_ets, seasonal_naive, ml_ridge, naive, stats_arima, moving_average, stream_ewm`
- artifact_count: `11`
- requested_backend: `arena`
- resolved_backend: `stats_ets`
- support_tier: `reviewed`
- latest_observed: `122.8400`
- projected_end: `122.7506`

Compared 7 backend(s) and routed the series to 'stats_ets'. Exported CSV, chart, card, markdown, and JSON artifacts.

## Intervals

- enabled: `False`
- method: `residual_heuristic`
- levels: `80, 90`

## Leaderboard

| backend_id | mae | rmse | mape | smape | coverage_80 | avg_width_80 | wnc_80 | coverage_90 | avg_width_90 | wnc_90 | backtest_horizon |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| stats_ets | 4.29779 | 4.87793 | 3.93689 | 3.96552 | 1 | 22.1064 | 5.33734 | 1 | 28.373 | 4.15851 | 14 |
| seasonal_naive | 5.15214 | 6.28645 | 4.49394 | 4.54409 | 0.857143 | 25.7118 | 3.93335 | 0.928571 | 33.0005 | 3.32 | 14 |
| ml_ridge | 9.41269 | 11.8294 | 7.55745 | 7.30946 | 1 | 151.031 | 0.781224 | 1 | 193.845 | 0.608679 | 14 |
| naive | 17.8893 | 22.5997 | 18.2099 | 16.0135 | 1 | 145.85 | 0.808979 | 1 | 187.194 | 0.630304 | 14 |
| stats_arima | 19.8505 | 22.1162 | 18.9063 | 17.7023 | 1 | 143.367 | 0.822988 | 1 | 184.008 | 0.641219 | 14 |
| moving_average | 20.265 | 22.4218 | 19.1821 | 18.0571 | 1 | 145.85 | 0.808979 | 1 | 187.194 | 0.630304 | 14 |
| stream_ewm | 22.0473 | 23.2015 | 20.0361 | 19.6419 | 1 | 172.918 | 0.682341 | 1 | 221.936 | 0.531636 | 14 |

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
