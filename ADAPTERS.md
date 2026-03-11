# Adapter strategy

`agentforecast` does not try to hide that some backends are optional adapters.

## Included runtime families

- native baseline logic
- native feature-based tabular logic
- native lightweight streaming logic
- statsmodels classical logic

## Optional adapters

- StatsForecast
- MLForecast
- River
- NeuralForecast
- AutoGluon-TimeSeries
- TabPFN

## Product principle

An adapter is useful only if it preserves the outer contract:

- same CLI shape
- same artifact pack shape
- same JSON result fields
- same agent/tool schema style

The moat is not “we also imported another framework”.
The moat is the **stable product surface over many frameworks**.


## v1.7 note

Optional adapters remain optional on purpose. The base path stays light, while heavier ecosystems are routed through extras so the first-run experience stays fast.
