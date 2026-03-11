# Honest switching guide

You probably should **not** switch from a specialized forecasting framework to `agentforecast` for pure model breadth.

You should consider `agentforecast` when you care more about:

- one command, many backends
- stable artifacts
- CLI friendliness
- agent/tool integration
- hosted gallery output
- quick cross-domain demos

## Mental model

- `sktime` / `Darts` / `StatsForecast` / `MLForecast` / `NeuralForecast` / `AutoGluon-TimeSeries` are forecasting ecosystems
- `agentforecast` is a **product layer over heterogeneous forecasting ecosystems**
