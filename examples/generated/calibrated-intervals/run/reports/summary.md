# airline_passengers

- backend_selected: `river_linear`
- candidate_backends: `river_linear`
- artifact_count: `10`
- latest_observed: `432.0000`
- projected_end: `338.8461`

Compared 1 backend(s) and routed the series to 'river_linear'. Exported CSV, chart, card, markdown, and JSON artifacts.

## Intervals

- enabled: `True`
- method: `river_jackknife`
- levels: `80, 90, 95`

## Leaderboard

| backend_id | mae | rmse | mape | smape | coverage_80 | avg_width_80 | wnc_80 | coverage_90 | avg_width_90 | wnc_90 | coverage_95 | avg_width_95 | wnc_95 | backtest_horizon |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| river_linear | 174.416 | 189.698 | 35.1843 | 43.4959 | 0.75 | 155.646 | 2.29446 | 0.833333 | 176.395 | 2.24953 | 0.833333 | 191.321 | 2.07403 | 12 |

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
