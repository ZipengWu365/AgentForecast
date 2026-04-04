# Support Policy

AgentForecast exposes three public support tiers.

## Reviewed

Reviewed surfaces are part of the `v1.8.0` reviewed release claim. They must have:

- direct tests in `tests/`
- documentation on GitHub and Pages
- stable artifact outputs
- explicit support metadata in the backend registry

Reviewed backends in this release:

- `naive`
- `seasonal_naive`
- `moving_average`
- `drift`
- `stats_arima`
- `stats_ets`
- `ml_ridge`
- `stream_ewm`

Reviewed surfaces:

- pack APIs: `forecast_dataframe`, `forecast_csv`, `forecast_url`, `forecast_dataset`, `shoot`
- research API: `OnlineForecaster`
- artifact outputs: `metadata.json`, `artifact_manifest.json`, CSV, plots, cards, markdown
- agent surface: `dispatch_tool_call`, `dispatch_jsonrpc`, `package_overview`, `list_reviewed_backends`, `backend_capabilities`

## Experimental

Experimental surfaces are visible and usable, but are not part of the reviewed paper claim.

- optional adapters such as `StatsForecast`, `MLForecast`, `River`, `TabPFN`
- non-reviewed backends such as `ml_xgboost`, `ml_histgb`, `stream_sgd`
- convenience workflows that depend on optional extras or looser runtime assumptions

These surfaces may have smoke coverage, but they are not promised as part of the reviewed release boundary.

## Planned

Planned surfaces are documented as roadmap or registry placeholders.

- `neural_nhits`
- `automl_autogluon`

They should not be described as stable current functionality in the README, paper, or release notes.
