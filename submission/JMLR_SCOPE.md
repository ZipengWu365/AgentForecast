# Scope

This release is scoped as a software-first scientific software submission.

## Primary claims

- reviewed pack API for turning one series into a publishable pack
- strict research API through `OnlineForecaster`
- stable publishable artifact contract
- stable tool and MCP consumption surface

## Explicit non-claims

- not a new forecasting method
- not a field-wide SOTA paper
- not a replacement for `sktime`, `StatsForecast`, `MLForecast`, or `River`
- not a claim that all optional adapters are reviewed
- not a claim that internal benchmark outputs are external evidence

## Reviewed backends in scope

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

## Annex

The streaming pilot appendix is included as a research annex. It is not part of the reviewed core claim.
