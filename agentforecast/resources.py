from __future__ import annotations

from typing import Any

from .backends import list_backend_capabilities, list_backends, list_backend_families
from .benchmark_hub import list_external_benchmarks
from .doctor import diagnose_environment
from .features import list_feature_presets
from .cases import _CASES
from .datasets import list_datasets
from .version import __version__


def describe_package(language: str = "en") -> dict[str, Any]:
    zh = language.lower().startswith("zh")
    if zh:
        headline = "一个包同时覆盖可发布 forecast pack 和 benchmark 友好的在线预测接口。"
        quickstart = [
            "python -m pip install agentforecast-1.7.0-py3-none-any.whl",
            "python -m agentforecast.cli doctor",
            "python -m agentforecast.cli shoot sales --outdir demo",
            "python -m agentforecast.cli benchmark-forecast data.csv --backend river_linear --horizons 12,36,72 --strict-mode",
            "python -m agentforecast.cli demo-gallery --outdir demo_gallery_runs --site-dir public_gallery/site",
            "python -m agentforecast.cli demo-examples --outdir examples/generated --site-dir examples/site",
        ]
    else:
        headline = "Publishable forecast packs plus benchmark-friendly online forecasting in one package."
        quickstart = [
            "python -m pip install agentforecast-1.7.0-py3-none-any.whl",
            "python -m agentforecast.cli doctor",
            "python -m agentforecast.cli shoot sales --outdir demo",
            "python -m agentforecast.cli benchmark-forecast data.csv --backend river_linear --horizons 12,36,72 --strict-mode",
            "python -m agentforecast.cli demo-gallery --outdir demo_gallery_runs --site-dir public_gallery/site",
            "python -m agentforecast.cli demo-examples --outdir examples/generated --site-dir examples/site",
        ]
    return {
        "name": "agentforecast",
        "version": __version__,
        "headline": headline,
        "value": "Use the pack surface for CSV/chart/report artifacts, or the benchmark surface for fit/predict/update online experiments with strict data handling and multi-horizon output.",
        "why_now": "Use it when you want one lightweight package that can serve both demo-pack workflows and reproducible benchmark adapters without reaching into private internals.",
        "quickstart": quickstart,
        "small_surface": [
            "OnlineForecaster",
            "forecast_benchmark_dataframe",
            "list_feature_presets",
            "shoot",
            "forecast_csv",
            "forecast_url",
            "forecast_dataset",
            "forecast_dir",
            "compare_backends",
            "forecast_stream_csv",
            "run_case",
            "build_hosted_site",
        ],
        "backend_families": [item["family"] for item in list_backend_families()],
    }


def api_catalog() -> list[dict[str, Any]]:
    return [
        {"name": "OnlineForecaster", "purpose": "Benchmark-first low-level API with fit/predict/update, strict_mode, lookback, and multi-horizon forecasting."},
        {"name": "forecast_benchmark_dataframe", "purpose": "One-shot benchmark forecast over a dataframe with horizons=[...] and recursive/direct mode."},
        {"name": "diagnose_environment", "purpose": "Report which backends are importable, why others are unavailable, and which workflows the environment supports."},
        {"name": "validate_series_frame", "purpose": "Inspect timestamps, duplicates, cadence, and strict-mode readiness without mutating the input."},
        {"name": "clean_series_frame", "purpose": "Opt in to the forgiving cleanup path that sorts, merges, fills, and normalizes a series frame."},
        {"name": "list_feature_presets", "purpose": "List benchmark-oriented feature presets such as traffic_5min, eeg, daily_climate, and flu."},
        {"name": "shoot", "purpose": "Camera mode. Auto-detect dataset id, case id, csv path, directory, or URL."},
        {"name": "forecast_csv", "purpose": "Forecast a local CSV with backend='auto' or a specific backend."},
        {"name": "forecast_url", "purpose": "Forecast a remote CSV URL."},
        {"name": "forecast_dataset", "purpose": "Run a wheel-safe bundled dataset demo."},
        {"name": "forecast_dir", "purpose": "Forecast multiple local CSV files in a folder."},
        {"name": "compare_backends_csv", "purpose": "Compare multiple backends on one local series and export leaderboard artifacts."},
        {"name": "forecast_stream_csv", "purpose": "Run a streaming backend and export drift diagnostics."},
        {"name": "run_case", "purpose": "Run a built-in cross-disciplinary or traffic-oriented case."},
        {"name": "build_hosted_site", "purpose": "Turn run directories into a static gallery site with HTML and feed.json."},
        {"name": "list_examples", "purpose": "List curated tutorial-grade runnable examples."},
        {"name": "demo_examples", "purpose": "Generate curated example runs and build a static examples site with real artifacts."},
        {"name": "build_examples_site", "purpose": "Build the tutorial-style examples site from previously generated example runs."},
    ]


def list_case_catalog(language: str = "en") -> list[dict[str, Any]]:
    return [case.to_dict(language) for case in _CASES]


def list_dataset_catalog(language: str = "en") -> list[dict[str, Any]]:
    return list_datasets(language)


def package_overview(language: str = "en") -> dict[str, Any]:
    return {
        **describe_package(language),
        "api_catalog": api_catalog(),
        "backends": list_backends(),
        "backend_capability_matrix": list_backend_capabilities(),
        "backend_families": list_backend_families(),
        "doctor": diagnose_environment(),
        "datasets": list_dataset_catalog(language),
        "cases": list_case_catalog(language),
        "external_benchmark_hub": list_external_benchmarks(),
        "feature_presets": list_feature_presets(),
        "hosted_gallery": {
            "description": "Static gallery builder for GitHub Pages or other simple hosting.",
            "commands": [
                "python -m agentforecast.cli demo-gallery --outdir demo_gallery_runs --site-dir public_gallery/site",
                "python -m agentforecast.cli build-gallery --runs-root demo_gallery_runs --site-dir public_gallery/site",
            ],
        },
        "examples_hub": {
            "description": "Tutorial-style examples hub with real runs, plots, source scripts, and copied artifacts.",
            "commands": [
                "python -m agentforecast.cli demo-examples --outdir examples/generated --site-dir examples/site",
                "python -m agentforecast.cli build-examples --runs-root examples/generated --site-dir examples/site",
                "python -m agentforecast.cli list-examples",
            ],
        },
    }
