# agentforecast

`agentforecast` 是一个 software-first 的 `forecast-to-publish` 轻量层：它把单条时间序列路由到异构后端，并稳定导出图表、卡片、CSV、Markdown、JSON 和 `artifact_manifest.json`。

这个版本不是新的 forecasting 方法，不宣称全领域最优，不替代 `sktime`、`StatsForecast`、`MLForecast` 或 `River`，也不把内部 benchmark 当成外部性能证据。

## 快速开始

源码安装：

```bash
python -m pip install .
python -m agentforecast.cli shoot sales --outdir demo
```

本地 wheel 安装：

```bash
python -m pip wheel . -w dist --no-deps
python -m pip install dist/agentforecast-1.9.0-py3-none-any.whl
```

环境体检与 streaming 附录：

```bash
python -m agentforecast.cli doctor
python -m agentforecast.cli stream-eval --outdir outputs
```

## 四个公开表面

- `Pack`：`forecast_dataframe`、`forecast_csv`、`forecast_dataset`、`shoot`
- `Research`：`OnlineForecaster` 和严格 backend 语义
- `Operations`：`doctor`、`build_hosted_site`、`stream-eval`
- `Agent`：`serve-tools`、`serve-mcp`、稳定 schema envelope

## v1.9.0 reviewed backends

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

## 文档入口

- 英文主 README: [README.md](README.md)
- Surface 边界: [SURFACES.md](SURFACES.md)
- 支持策略: [SUPPORT_POLICY.md](SUPPORT_POLICY.md)
- reviewed surface: [REVIEWED_SURFACE.md](REVIEWED_SURFACE.md)
- backend 注册表: [BACKENDS.md](BACKENDS.md)
- benchmark 边界: [BENCHMARK_HUB.md](BENCHMARK_HUB.md)
- agent/tool/MCP 契约: [AGENT_SURFACE.md](AGENT_SURFACE.md)
- schema/version 规则: [SCHEMA_POLICY.md](SCHEMA_POLICY.md)
- 验证证据: [VALIDATION.md](VALIDATION.md)
- 投稿入口: [submission/JMLR_SCOPE.md](submission/JMLR_SCOPE.md)
