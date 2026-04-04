# airline_passengers

- backend_selected: `stats_ets`
- candidate_backends: `stats_ets, ml_ridge, moving_average, stats_arima, stream_ewm, naive`
- artifact_count: `11`
- requested_backend: `arena`
- resolved_backend: `stats_ets`
- support_tier: `reviewed`
- latest_observed: `432.0000`
- projected_end: `471.0526`

Compared 6 backend(s) and routed the series to 'stats_ets'. Exported CSV, chart, card, markdown, and JSON artifacts.

## Intervals

- enabled: `False`
- method: `residual_heuristic`
- levels: `80, 90`

## Leaderboard

| backend_id | mae | rmse | mape | smape | coverage_80 | avg_width_80 | wnc_80 | coverage_90 | avg_width_90 | wnc_90 | backtest_horizon |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| stats_ets | 13.3822 | 16.9811 | 2.80314 | 2.79587 | 0.916667 | 70.4924 | 6.19196 | 0.916667 | 90.4752 | 4.82437 | 12 |
| ml_ridge | 36.0792 | 51.6593 | 8.36643 | 7.69363 | 0.916667 | 181.24 | 2.40834 | 1 | 232.616 | 2.047 | 12 |
| moving_average | 58.0952 | 76.2865 | 11.5693 | 11.9736 | 1 | 436.27 | 1.09145 | 1 | 559.941 | 0.850388 | 12 |
| stats_arima | 66.2417 | 91.2288 | 12.462 | 13.7923 | 1 | 439.554 | 1.08329 | 1 | 564.156 | 0.844034 | 12 |
| stream_ewm | 67.2806 | 92.1292 | 12.683 | 14.0379 | 1 | 470.22 | 1.01265 | 1 | 603.516 | 0.788988 | 12 |
| naive | 76 | 102.977 | 14.2513 | 16.1208 | 1 | 436.27 | 1.09145 | 1 | 559.941 | 0.850388 | 12 |

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
