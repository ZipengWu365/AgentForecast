
from __future__ import annotations

from typing import Any

_BENCHMARKS = [
    {
        "name": "Monash / ForecastingData repository",
        "url": "https://forecastingdata.org/",
        "kind": "dataset hub",
        "notes": "Public repository of time-series datasets plus baseline evaluation pages.",
    },
    {
        "name": "Monash baseline evaluation results",
        "url": "https://forecastingdata.org/RMSSE.html",
        "kind": "baseline results",
        "notes": "Baseline evaluation page hosted by the Monash forecasting repository.",
    },
    {
        "name": "M4 competition",
        "url": "https://www.unic.ac.cy/iff/research/forecasting/m-competitions/m4/",
        "kind": "competition",
        "notes": "Classic multi-domain forecasting competition.",
    },
    {
        "name": "M5 competition",
        "url": "https://www.unic.ac.cy/iff/research/forecasting/m-competitions/m5/",
        "kind": "competition",
        "notes": "Retail forecasting benchmark with exogenous structure and hierarchy.",
    },
    {
        "name": "OpenTS-Bench / OpenTS",
        "url": "https://decisionintelligence.github.io/OpenTS/",
        "kind": "leaderboard hub",
        "notes": "OpenTS benchmark and leaderboard surface for time-series forecasting and related tasks.",
    },
    {
        "name": "TFB repository",
        "url": "https://github.com/decisionintelligence/TFB",
        "kind": "benchmark codebase",
        "notes": "Comprehensive and fair benchmarking toolkit for time-series forecasting methods.",
    },
    {
        "name": "GIFT-Eval repository",
        "url": "https://github.com/SalesforceAIResearch/gift-eval",
        "kind": "benchmark",
        "notes": "Foundation-model oriented time-series benchmark with code and data.",
    },
    {
        "name": "GIFT-Eval public leaderboard",
        "url": "https://huggingface.co/spaces/Salesforce/GIFT-Eval",
        "kind": "leaderboard",
        "notes": "Interactive public leaderboard for GIFT-Eval.",
    },
    {
        "name": "ForecastBench baseline leaderboard",
        "url": "https://www.forecastbench.org/baseline/",
        "kind": "leaderboard",
        "notes": "Out-of-the-box AI forecasting leaderboard.",
    },
    {
        "name": "ForecastBench tournament leaderboard",
        "url": "https://www.forecastbench.org/tournament/",
        "kind": "leaderboard",
        "notes": "Tool-augmented frontier leaderboard for AI forecasting systems.",
    },
]


def list_external_benchmarks() -> list[dict[str, Any]]:
    return list(_BENCHMARKS)
