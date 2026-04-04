# Reviewed Surface

This file defines the exact surface covered by the `agentforecast v1.8.0` reviewed release.

## Core APIs

- `forecast_dataframe`
- `forecast_csv`
- `forecast_url`
- `forecast_dataset`
- `shoot`
- `build_hosted_site`
- `OnlineForecaster`

## Reviewed backends

- `naive`
- `seasonal_naive`
- `moving_average`
- `drift`
- `stats_arima`
- `stats_ets`
- `ml_ridge`
- `stream_ewm`

## Reviewed artifact outputs

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
- `meta/artifact_manifest.json`

## Reviewed agent surface

- tool server error contract
- MCP `resources/list`, `resources/read`, `tools/list`, `tools/call`
- resource payloads for package overview and backend capabilities

## Outside the reviewed claim

- optional adapters that require extra dependencies and only smoke coverage
- planned adapters without shipped runtime implementations
- any statement that compares AgentForecast as a superior general-purpose framework against specialized forecasting libraries
