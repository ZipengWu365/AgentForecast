from __future__ import annotations

from typing import Any

from .backends import backend_capabilities, list_backends, list_backend_families, list_reviewed_backends
from .benchmark_hub import list_external_benchmarks
from .cases import _CASES
from .datasets import list_datasets
from .version import __version__


REPOSITORY_URL = "https://github.com/ZipengWu365/AgentForecast"
DOCS_URL = "https://zipengwu365.github.io/AgentForecast/"
GALLERY_URL = "https://zipengwu365.github.io/AgentForecast/gallery/"
PAPER_URL = "https://zipengwu365.github.io/AgentForecast/papers/jmlr-mloss/"


def describe_package(language: str = "en") -> dict[str, Any]:
    zh = language.lower().startswith("zh")
    if zh:
        headline = "把任意 time series 变成可发布 forecast pack 的 reviewed forecast-to-publish layer。"
        quickstart = [
            "python -m pip install .",
            "python -m agentforecast.cli shoot sales --outdir demo",
            "python -m pip wheel . -w dist --no-deps",
            "python -m pip install dist/agentforecast-1.8.0-py3-none-any.whl",
            "python -m agentforecast.cli demo-gallery --outdir public_gallery/demo_runs --site-dir public_gallery/site",
        ]
    else:
        headline = "A reviewed forecast-to-publish layer for turning time series into publishable forecast packs."
        quickstart = [
            "python -m pip install .",
            "python -m agentforecast.cli shoot sales --outdir demo",
            "python -m pip wheel . -w dist --no-deps",
            "python -m pip install dist/agentforecast-1.8.0-py3-none-any.whl",
            "python -m agentforecast.cli demo-gallery --outdir public_gallery/demo_runs --site-dir public_gallery/site",
        ]
    return {
        "name": "agentforecast",
        "version": __version__,
        "headline": headline,
        "value": "A small forecasting surface over reviewed and experimental backends that exports CSV, chart, card, markdown, JSON, and a stable artifact manifest.",
        "why_now": "Use it when you want a smaller product surface than a full forecasting framework, but a richer output contract than a bare model API.",
        "quickstart": quickstart,
        "public_urls": {
            "repository": REPOSITORY_URL,
            "documentation": DOCS_URL,
            "gallery": GALLERY_URL,
            "paper_entry": PAPER_URL,
        },
        "support_policy": {
            "reviewed": "Supported in tests, docs, and the JMLR reviewed release claim.",
            "experimental": "Exposed publicly but not part of the reviewed paper claim.",
            "planned": "Documented as roadmap or registry placeholders, not in the reviewed release claim.",
        },
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
            "OnlineForecaster",
        ],
        "backend_families": [item["family"] for item in list_backend_families()],
        "reviewed_backends": [item["backend_id"] for item in list_reviewed_backends()],
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
        {"name": "OnlineForecaster", "purpose": "Research-oriented strict backend wrapper for benchmark-safe forecasting and backtests."},
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
        "reviewed_backends": list_reviewed_backends(),
        "backend_capabilities": {item["backend_id"]: backend_capabilities(item["backend_id"]) for item in list_backends()},
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
        "examples_hub": {
            "description": "Tutorial-style examples hub with real runs, plots, source scripts, and copied artifacts.",
            "commands": [
                "python -m agentforecast.cli demo-examples --outdir examples/generated --site-dir examples/site",
                "python -m agentforecast.cli build-examples --runs-root examples/generated --site-dir examples/site",
                "python -m agentforecast.cli list-examples",
            ],
        },
    }
