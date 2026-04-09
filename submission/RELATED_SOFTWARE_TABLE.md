# Related Software

| Project | Primary role | What AgentForecast does differently | Non-claim boundary |
|---|---|---|---|
| `sktime` | broad unified time-series ML framework | smaller forecast-to-publish surface with explicit artifact contract | does not replace `sktime` |
| `StatsForecast` | large-scale statistical forecasting | reviewed software layer on top of a narrower public surface | does not replace `StatsForecast`; adapters remain experimental here |
| `MLForecast` | scalable ML forecasting | uses one reviewed `MLForecast` adapter inside a larger publishable-pack system | does not replace `MLForecast` |
| `River` | online and streaming ML | uses reviewed River adapters inside a reproducible artifact-producing layer | does not replace `River` |

The paper should frame these projects as neighboring ecosystems, not as defeated baselines.
