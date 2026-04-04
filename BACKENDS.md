# Backends

AgentForecast groups backends by family and exposes support metadata in code through `list_backends()`, `list_reviewed_backends()`, and `backend_capabilities()`.

## Reviewed

- `naive`
- `seasonal_naive`
- `moving_average`
- `drift`
- `stats_arima`
- `stats_ets`
- `ml_ridge`
- `stream_ewm`

## Experimental

- `statsforecast_autoarima`
- `statsforecast_autoets`
- `ml_histgb`
- `ml_xgboost`
- `ml_lightgbm`
- `ml_catboost`
- `mlforecast_linear`
- `mlforecast_xgboost`
- `stream_sgd`
- `river_linear`
- `river_snarimax`
- `river_holtwinters`
- `tabpfn_regression`

## Planned

- `neural_nhits`
- `automl_autogluon`

## Capability fields

Each backend capability record includes:

- `tier`
- `tested`
- `strict_benchmark_eligible`
- `dependencies`
- `dependency_state`
- `supports_exogenous`
- `supports_online_update`
