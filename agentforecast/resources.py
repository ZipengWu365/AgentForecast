from __future__ import annotations

from typing import Any

from .backends import list_backends, list_backend_families
from .benchmark_hub import list_external_benchmarks
from .cases import _CASES
from .datasets import list_datasets
from .version import __version__


def describe_package(language: str = "en") -> dict[str, Any]:
    zh = language.lower().startswith("zh")
    if zh:
        headline = "用 one command 把任意 time series 变成可发布的 forecast pack。"
        quickstart = [
            "python -m pip install agentforecast-1.7.0-py3-none-any.whl",
            "python -m agentforecast.cli shoot sales --outdir demo",
            "python -m agentforecast.cli demo-gallery --outdir demo_gallery_runs --site-dir public_gallery/site",
        ]
    else:
        headline = "Turn any time series into a publishable forecast pack in one command."
        quickstart = [
            "python -m pip install agentforecast-1.7.0-py3-none-any.whl",
            "python -m agentforecast.cli shoot sales --outdir demo",
            "python -m agentforecast.cli demo-gallery --outdir demo_gallery_runs --site-dir public_gallery/site",
        ]
    return {
        "name": "agentforecast",
        "version": __version__,
        "headline": headline,
        "value": "One command routes a time series through baseline, classical, tabular, streaming, or optional adapter backends and exports CSV, chart, card, markdown, and JSON artifacts.",
        "why_now": "Use it when you want a smaller product surface than a full forecasting framework, but a richer output contract than a bare model API.",
        "quickstart": quickstart,
        "small_surface": [
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
        {"name": "shoot", "purpose": "Camera mode. Auto-detect dataset id, case id, csv path, directory, or URL."},
        {"name": "forecast_csv", "purpose": "Forecast a local CSV with backend='auto' or a specific backend."},
        {"name": "forecast_url", "purpose": "Forecast a remote CSV URL."},
        {"name": "forecast_dataset", "purpose": "Run a wheel-safe bundled dataset demo."},
        {"name": "forecast_dir", "purpose": "Forecast multiple local CSV files in a folder."},
        {"name": "compare_backends_csv", "purpose": "Compare multiple backends on one local series and export leaderboard artifacts."},
        {"name": "forecast_stream_csv", "purpose": "Run a streaming backend and export drift diagnostics."},
        {"name": "run_case", "purpose": "Run a built-in cross-disciplinary or traffic-oriented case."},
        {"name": "build_hosted_site", "purpose": "Turn run directories into a static gallery site with HTML and feed.json."},
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
        "backend_families": list_backend_families(),
        "datasets": list_dataset_catalog(language),
        "cases": list_case_catalog(language),
        "external_benchmark_hub": list_external_benchmarks(),
        "hosted_gallery": {
            "description": "Static gallery builder for GitHub Pages or other simple hosting.",
            "commands": [
                "python -m agentforecast.cli demo-gallery --outdir demo_gallery_runs --site-dir public_gallery/site",
                "python -m agentforecast.cli build-gallery --runs-root demo_gallery_runs --site-dir public_gallery/site",
            ],
        },
    }
