# Backend Registry

The backend registry is the code-level source of truth for support tier, test status, dependency requirements, exogenous support, online-update support, and strict benchmark eligibility.

## Reviewed in v1.9.0

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

These are the only backends covered simultaneously by code metadata, tests, docs, Pages, and the reviewed release claim.

## Experimental

- `statsforecast_autoarima`
- `statsforecast_autoets`
- `ml_histgb`
- `ml_xgboost`
- `ml_lightgbm`
- `ml_catboost`
- `mlforecast_xgboost`
- `stream_sgd`
- `river_holtwinters`
- `tabpfn_regression`

Experimental means public and discoverable, but not part of the reviewed software claim.

## Planned

- `neural_nhits`
- `automl_autogluon`

Planned means documented as roadmap or placeholders only.

## Promotion rule

A backend only moves into `reviewed` when it satisfies all of the following in the same release:

- end-to-end pack generation succeeds
- strict backend identity is preserved
- `metadata.json` and `artifact_manifest.json` record the right provenance
- tool and MCP surfaces can discover the backend
- docs, Pages, submission files, and validation truth tables all match
