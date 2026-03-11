# transit_demand_shock

- backend_selected: `stats_ets`
- candidate_backends: `stats_ets, seasonal_naive, ml_ridge, naive, stats_arima, moving_average, stream_ewm`
- artifact_count: `10`
- latest_observed: `122.8400`
- projected_end: `122.7505`

Compared 7 backend(s) and routed the series to 'stats_ets'. Exported CSV, chart, card, markdown, and JSON artifacts.

## Leaderboard

| backend_id | mae | rmse | mape | smape | backtest_horizon |
| --- | --- | --- | --- | --- | --- |
| stats_ets | 4.29824 | 4.87838 | 3.93728 | 3.96596 | 14 |
| seasonal_naive | 5.15214 | 6.28645 | 4.49394 | 4.54409 | 14 |
| ml_ridge | 9.41269 | 11.8294 | 7.55745 | 7.30946 | 14 |
| naive | 17.8893 | 22.5997 | 18.2099 | 16.0135 | 14 |
| stats_arima | 19.8505 | 22.1162 | 18.9063 | 17.7023 | 14 |
| moving_average | 20.265 | 22.4218 | 19.1821 | 18.0571 | 14 |
| stream_ewm | 22.0473 | 23.2015 | 20.0361 | 19.6419 | 14 |

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
