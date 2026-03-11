# sales

- backend_selected: `stats_ets`
- candidate_backends: `stats_ets, ml_ridge, seasonal_naive, stats_arima, naive, moving_average, stream_ewm`
- artifact_count: `10`
- latest_observed: `164.0400`
- projected_end: `168.9935`

Compared 7 backend(s) and routed the series to 'stats_ets'. Exported CSV, chart, card, markdown, and JSON artifacts.

## Leaderboard

| backend_id | mae | rmse | mape | smape | backtest_horizon |
| --- | --- | --- | --- | --- | --- |
| stats_ets | 2.66825 | 3.34 | 1.66006 | 1.66291 | 14 |
| ml_ridge | 3.33187 | 4.0847 | 2.06825 | 2.09282 | 14 |
| seasonal_naive | 4.40929 | 5.81541 | 2.72586 | 2.78914 | 14 |
| stats_arima | 6.71996 | 8.42389 | 4.26758 | 4.15883 | 14 |
| naive | 7.06929 | 8.14532 | 4.32582 | 4.38346 | 14 |
| moving_average | 7.38337 | 8.44123 | 4.50356 | 4.58144 | 14 |
| stream_ewm | 8.83558 | 10.3431 | 5.32818 | 5.50834 | 14 |

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
