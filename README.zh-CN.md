# agentforecast

**AgentForecast 是一个建立在稳定 forecasting core 之上的轻量 forecast-to-publish layer，并额外提供 research 与 agent/tooling surface。**

`agentforecast` 是一个 **多后端、agent-friendly、output-first** 的 forecast-to-publish layer。

它同时做三件事：

1. 用很小的调用面封装多种 forecasting backend
2. 自动比较或选择 backend
3. 导出 `CSV + chart + card + markdown + JSON`

## 最短上手

```bash
python -m pip install agentforecast-1.7.0-py3-none-any.whl
python -m agentforecast.cli doctor
python -m agentforecast.cli shoot sales --outdir demo
```

生成 hosted gallery：

```bash
python -m agentforecast.cli demo-gallery --outdir demo_gallery_runs --site-dir public_gallery/site
```

## 现在支持什么

- lean base path：`naive / seasonal_naive / moving_average / drift / stream_ewm`
- classical：`stats_arima / stats_ets / StatsForecast adapters`
- tabular：`ml_ridge / ml_histgb / ml_xgboost / MLForecast adapters`
- streaming：`stream_sgd / stream_ewm / River adapters`
- optional high-end：`NHITS / AutoGluon / TabPFN`

## 安装矩阵

| 角色 | 命令 | 适合场景 |
| --- | --- | --- |
| 入门 / pack 用户 | `pip install agentforecast` | 一次性 forecast pack 与自动路由 |
| research / benchmark | `pip install "agentforecast[stats,ml]"` | 严格 benchmark、对比实验、`OnlineForecaster` |
| streaming / operations | `pip install "agentforecast[stream]"` | River 流式 backend 与监控场景 |
| 全量可选栈 | `pip install "agentforecast[all]"` | 最广的 adapter 覆盖 |

## backend 能力矩阵

| Backend | Extra | Tier | Streaming | Exogenous | Conformal | Direct | Recursive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `naive` | base | stable | 否 | 否 | 否 | 否 | 是 |
| `stats_ets` | stats | stable | 否 | 否 | 否 | 否 | 是 |
| `ml_ridge` | ml | stable | 否 | 是 | 否 | 是 | 是 |
| `stream_ewm` | base | stable | 是 | 否 | 否 | 否 | 是 |
| `river_linear` | stream | beta | 是 | 是 | 是 | 是 | 是 |
| `stream_sgd` | ml | experimental | 是 | 是 | 否 | 否 | 是 |

## benchmark 首选 API

如果你把 `agentforecast` 当成论文里的正式 baseline，优先用低层 `OnlineForecaster`，不要只靠 pack 型 helper。

```python
from agentforecast import OnlineForecaster

forecaster = OnlineForecaster(
    backend="river_linear",
    lookback=336,
    horizons=[1, 3, 6, 12],
    strict_mode=True,
    feature_preset="benchmark_auto",
    mode="recursive",
)
forecaster.fit(initial_history)
yhat = forecaster.predict()
forecaster.update(y_new)
```

这套 benchmark API 的关键约定是：

- `fit / predict / update` 是公开 contract
- `horizons=[...]` 一次表达一组评测 horizon
- `lookback` 或 `max_history` 显式限制可见历史
- `strict_mode=True` 关闭插值、重复时间戳合并、隐式补齐等修复
- `mode="recursive"` 表示逐步 rollout，`mode="direct"` 表示按 horizon 直接输出
- `benchmark_auto / traffic_5min / eeg / daily_climate / flu` 这类 preset 比通用 demo 默认值更适合做实验

## 它的核心价值

不是做最大的 forecasting framework，
而是把异构 forecasting 生态压成一个统一的 **agent-friendly forecast OS layer**，
并且把结果统一输出成可发布的 artifact pack。

如果你的目标是严格 benchmark，记得把 pack 型 demo surface 和低层 benchmark surface 分开看。

## 重点文档

- [BACKENDS.md](BACKENDS.md)
- [BENCHMARK_HUB.md](BENCHMARK_HUB.md)
- [CROSS_DISCIPLINARY_GUIDE.md](CROSS_DISCIPLINARY_GUIDE.md)
- [HONEST_SWITCHING_GUIDE.md](HONEST_SWITCHING_GUIDE.md)
- [HOSTED_GALLERY_GUIDE.md](HOSTED_GALLERY_GUIDE.md)
- [ADAPTERS.md](ADAPTERS.md)


## 这一版修了什么

- base quickstart 不再隐式依赖 `tabulate`
- 推荐继续使用 `python -m agentforecast.cli ...` 作为最稳妥的复制运行路径
- 仓库根目录补齐了标准开源 trust files
- internal benchmark 与 external benchmark hub 明确分开叙述
