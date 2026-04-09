# Support Policy

`agentforecast` uses three public support tiers.

## Tiers

- `reviewed`: in tests, in docs, in Pages, in submission evidence, and in the release claim
- `experimental`: public and discoverable, but outside the reviewed claim
- `planned`: roadmap or registry placeholders, not current release functionality

## Reviewed boundary for v1.9.0

Reviewed surfaces:

- reviewed pack API
- strict research API through `OnlineForecaster`
- stable publishable artifact contract
- stable tool and MCP consumption surface
- reviewed operations surface via `doctor`

Reviewed backends:

- `naive`
- `seasonal_naive`
- `moving_average`
- `drift`
- `stats_arima`
- `stats_ets`
- `ml_ridge`
- `mlforecast_linear`
- `stream_ewm`
- `river_linear`
- `river_snarimax`

## Explicit non-promotion in v1.9.0

Still experimental:

- all `StatsForecast` adapters
- `mlforecast_xgboost`
- `stream_sgd`
- `river_holtwinters`
- `tabpfn_regression`

Still planned:

- `neural_nhits`
- `automl_autogluon`

## Streaming note

The new streaming pilot is a research annex. It is not part of the reviewed core claim and should not be interpreted as a general superiority statement for streaming models.
