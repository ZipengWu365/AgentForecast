
# Backends

`agentforecast` groups forecasting methods into a few backend families so users and agents do not need to memorize each framework's API.

## Families

- **baseline**: fastest path for smoke tests and small, low-risk demos
- **classical**: ARIMA / ETS style models for compact univariate forecasting
- **tabular**: lag-window regression with Ridge / boosting style models
- **streaming**: online updates and drift-aware monitoring
- **deep**: optional long-horizon or larger-scale neural backends
- **automl**: optional higher-level search or ensembling backends
- **tabpfn**: optional advanced regression backend with separate license constraints

## When to use what

### Use `strategy=fast`
Use this when you want the quickest publishable pack, a first look at a local CSV, or a vibe-coding demo.

### Use `strategy=accurate`
Use this when you want a broader candidate set across classical and tabular backends.

### Use `strategy=streaming`
Use this for live monitoring, concept drift, operational dashboards, and cases where the model should update as new points arrive.

### Use `strategy=low_data`
Use this when the series is short or when simple linear / classical structure is more trustworthy than heavier models.

### Use `strategy=long_horizon`
Use this when the forecast horizon is long relative to the history and you want methods that cope better with multi-step extrapolation.

## Concrete heuristics

- If your series has **< 200 observations**, start with `low_data`.
- If your workflow is **ops monitoring or alerting**, start with `streaming`.
- If you have **clean exogenous columns** in the CSV, try `accurate` or explicit tabular backends.
- If you are reproducing long-horizon academic settings such as `96/192/336/720`, deep backends become more relevant.
- If you just want a report in under 10 seconds, stay on the lean base path.

## Honest warning

Heavier backends are not automatically better. In many real business or scientific series, `Ridge`, `ETS`, or `ARIMA` can beat a more complex model once installation cost, calibration, and robustness matter.
