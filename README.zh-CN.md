# agentforecast

**用 one command 调度 classical、tabular、streaming 和 optional adapters，把任意 time series 变成可发布的 forecast pack。**

`agentforecast` 是一个 **多后端、agent-friendly、output-first** 的 forecast-to-publish layer。

它同时做三件事：

1. 用很小的调用面封装多种 forecasting backend
2. 自动比较或选择 backend
3. 导出 `CSV + chart + card + markdown + JSON`

## 最短上手

```bash
python -m pip install agentforecast-1.7.0-py3-none-any.whl
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

## 它的核心价值

不是做最大的 forecasting framework，
而是把异构 forecasting 生态压成一个统一的 **agent-friendly forecast OS layer**，
并且把结果统一输出成可发布的 artifact pack。

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
