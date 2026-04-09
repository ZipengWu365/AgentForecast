from __future__ import annotations

import importlib.util
from typing import Any

from .backends import is_backend_available, list_reviewed_backends


_PROMOTED_BACKENDS = ("mlforecast_linear", "river_linear", "river_snarimax")
_DOCS_URL = "https://zipengwu365.github.io/AgentForecast/"
_GALLERY_URL = "https://zipengwu365.github.io/AgentForecast/gallery/"
_PAPER_URL = "https://zipengwu365.github.io/AgentForecast/papers/jmlr-mloss/"
_REPOSITORY_URL = "https://github.com/ZipengWu365/AgentForecast"
_EXTRA_MODULES = {
    "stats": ("statsmodels", "statsforecast"),
    "ml": ("sklearn", "mlforecast"),
    "stream": ("river",),
    "features": ("tsfresh",),
    "deep": ("neuralforecast",),
    "automl": ("autogluon.timeseries",),
    "tabpfn": ("tabpfn",),
}


def _has(module: str) -> bool:
    try:
        return importlib.util.find_spec(module) is not None
    except ModuleNotFoundError:
        return False


def _extra_status() -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for extra_name, modules in _EXTRA_MODULES.items():
        module_state = {module: _has(module) for module in modules}
        payload[extra_name] = {
            "installed": all(module_state.values()),
            "modules": module_state,
        }
    return payload


def doctor() -> dict[str, Any]:
    extra_status = _extra_status()
    installed_extras = [name for name, item in extra_status.items() if item["installed"]]
    missing_promoted = [backend_id for backend_id in _PROMOTED_BACKENDS if not is_backend_available(backend_id)]
    reviewed_backend_ids = [item["backend_id"] for item in list_reviewed_backends()]
    available_workflows: list[dict[str, str]] = [
        {
            "workflow_id": "pack",
            "label": "Reviewed pack generation",
            "command": "python -m agentforecast.cli shoot sales --outdir demo",
        },
        {
            "workflow_id": "gallery",
            "label": "Static Pages gallery build",
            "command": "python -m agentforecast.cli demo-gallery --outdir public_gallery/demo_runs --site-dir public_gallery/site",
        },
        {
            "workflow_id": "agent_surface",
            "label": "Tool and MCP inspection",
            "command": "python -m agentforecast.cli doctor",
        },
    ]
    if is_backend_available("mlforecast_linear"):
        available_workflows.append(
            {
                "workflow_id": "reviewed_mlforecast",
                "label": "Reviewed MLForecast candidate run",
                "command": "python -m agentforecast.cli forecast-csv agentforecast/package_data/public_examples/monthly_car_sales.csv --backend mlforecast_linear --outdir demo",
            }
        )
    if is_backend_available("river_linear") and is_backend_available("river_snarimax"):
        available_workflows.append(
            {
                "workflow_id": "reviewed_river",
                "label": "Reviewed River candidate run",
                "command": "python -m agentforecast.cli forecast-stream agentforecast/package_data/public_examples/daily_min_temperatures.csv --backend river_snarimax --outdir demo",
            }
        )
        available_workflows.append(
            {
                "workflow_id": "streaming_pilot",
                "label": "Streaming evaluation pilot",
                "command": "python -m agentforecast.cli stream-eval --outdir outputs",
            }
        )

    if missing_promoted:
        recommended_next_command = "python -m pip install .[dev,ml,stream]"
    elif any(item["workflow_id"] == "streaming_pilot" for item in available_workflows):
        recommended_next_command = "python -m agentforecast.cli stream-eval --outdir outputs"
    else:
        recommended_next_command = "python -m agentforecast.cli shoot sales --outdir demo"

    return {
        "kind": "agentforecast.doctor_report",
        "installed_extras": installed_extras,
        "extra_status": extra_status,
        "reviewed_backends": reviewed_backend_ids,
        "reviewed_workflows_available": available_workflows,
        "missing_promoted_backends": missing_promoted,
        "recommended_next_command": recommended_next_command,
        "links": {
            "docs": _DOCS_URL,
            "gallery": _GALLERY_URL,
            "paper_entry": _PAPER_URL,
            "repository": _REPOSITORY_URL,
        },
        "warnings": [],
        "resolution": None,
        "artifacts": [],
    }
