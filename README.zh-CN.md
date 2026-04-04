# agentforecast

**面向异构 forecasting backend 的 reviewed forecast-to-publish layer。**

公开入口：

- [文档](https://zipengwu365.github.io/AgentForecast/)
- [Gallery](https://zipengwu365.github.io/AgentForecast/gallery/)
- [JMLR 审稿入口](https://zipengwu365.github.io/AgentForecast/papers/jmlr-mloss/)
- [Issues](https://github.com/ZipengWu365/AgentForecast/issues)

`agentforecast` 的定位不是“大而全的 forecasting framework”，而是把多种 backend 收缩成一个小而稳定的工作流层，并统一导出：

- CSV
- chart
- card
- markdown
- JSON
- artifact manifest

它不替代 `sktime`、`StatsForecast`、`MLForecast`、`River` 这类 specialized framework；它负责统一路由、产物和 agent/tool 消费接口。

## 快速开始

源码安装：

```bash
python -m pip install .
python -m agentforecast.cli shoot sales --outdir demo
```

本地 wheel 安装：

```bash
python -m pip wheel . -w dist --no-deps
python -m pip install dist/agentforecast-1.8.0-py3-none-any.whl
python -m agentforecast.cli shoot sales --outdir demo
```

GitHub Release 资产安装：

```bash
python -m pip install <downloaded-release-wheel>.whl
python -m agentforecast.cli shoot sales --outdir demo
```

## 四个 surface

- `Pack`：`forecast_dataframe`、`forecast_csv`、`forecast_url`、`forecast_dataset`、`shoot`
- `Research`：`OnlineForecaster`，默认严格 backend 解析，避免静默替换
- `Artifacts`：`meta/metadata.json`、`meta/artifact_manifest.json`、图表、卡片、CSV、markdown
- `Agent`：tool / MCP server 与稳定 JSON payload

## 支持分层

- `Reviewed`：纳入测试、文档和论文 claim
- `Experimental`：公开暴露，但不纳入 reviewed release claim
- `Planned`：路线图或占位，不算当前 reviewed surface

当前 reviewed backends：

- `naive`
- `seasonal_naive`
- `moving_average`
- `drift`
- `stats_arima`
- `stats_ets`
- `ml_ridge`
- `stream_ewm`

详见：

- [SUPPORT_POLICY.md](SUPPORT_POLICY.md)
- [REVIEWED_SURFACE.md](REVIEWED_SURFACE.md)
- [BACKENDS.md](BACKENDS.md)
- [BENCHMARK_SEMANTICS.md](BENCHMARK_SEMANTICS.md)
- [ARTIFACT_SCHEMA.md](ARTIFACT_SCHEMA.md)

## 可选 extras

```bash
python -m pip install ".[stats]"
python -m pip install ".[ml]"
python -m pip install ".[stream]"
python -m pip install ".[features]"
python -m pip install ".[deep]"
python -m pip install ".[automl]"
python -m pip install ".[tabpfn]"
```

Optional adapters 默认不属于 reviewed claim，除非它们进入测试和 support policy。

## 社区与治理

- Bug：GitHub Issues
- Feature request：GitHub Issues
- 使用讨论和 showcase：公共仓库启用后进入 GitHub Discussions

补充文档：

- [COMMUNITY.md](COMMUNITY.md)
- [GOVERNANCE.md](GOVERNANCE.md)
- [submission/JMLR_SCOPE.md](submission/JMLR_SCOPE.md)
- [submission/REPRODUCTION.md](submission/REPRODUCTION.md)
