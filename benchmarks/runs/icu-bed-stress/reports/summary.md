# icu_bed_stress

- backend_selected: `ml_ridge`
- candidate_backends: `ml_ridge, moving_average, seasonal_naive, stats_arima, naive, stats_ets, stream_ewm`
- artifact_count: `10`
- latest_observed: `93.4200`
- projected_end: `89.0699`

Compared 7 backend(s) and routed the series to 'ml_ridge'. Exported CSV, chart, card, markdown, and JSON artifacts.

## Leaderboard

| backend_id | mae | rmse | mape | smape | backtest_horizon |
| --- | --- | --- | --- | --- | --- |
| ml_ridge | 2.72892 | 3.91303 | 3.13165 | 3.03682 | 14 |
| moving_average | 3.43071 | 4.86646 | 3.95242 | 3.79889 | 14 |
| seasonal_naive | 4.94357 | 5.71633 | 5.54603 | 5.39135 | 14 |
| stats_arima | 5.93272 | 7.00893 | 6.73459 | 6.42297 | 14 |
| naive | 6.11357 | 7.16251 | 6.9345 | 6.60983 | 14 |
| stats_ets | 6.67551 | 7.6842 | 7.55709 | 7.1866 | 14 |
| stream_ewm | 10.6529 | 11.9451 | 11.9962 | 11.1404 | 14 |

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
