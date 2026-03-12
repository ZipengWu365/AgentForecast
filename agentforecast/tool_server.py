from __future__ import annotations

import json
import sys
from typing import Any

from .errors import AgentForecastError
from .examples_hub import build_examples_site, demo_examples, list_examples
from .hosted import build_hosted_site
from .local import (
    compare_backends_csv,
    forecast_csv,
    forecast_dataset,
    forecast_dir,
    forecast_stream_csv,
    forecast_url,
    shoot,
)
from .live import run_case, list_cases
from .datasets import list_datasets
from .backends import list_backends, list_backend_families, route_backends
from .resources import package_overview
from .version import __version__


_TOOL_VERSION = __version__
_ERROR_SCHEMA = "package://agentforecast/package_data/schemas/error.schema.json"
_ERROR_KIND = "agentforecast.error"
_ERROR_SCHEMA_VERSION = "1.1.0"


def _tool_catalog() -> list[dict[str, Any]]:
    return [
        {"name": "describe_package", "description": "Describe the package and safest quickstart."},
        {"name": "shoot", "description": "Camera mode for datasets, cases, local CSV, directories, or CSV URLs."},
        {"name": "forecast_dataset", "description": "Forecast a bundled dataset."},
        {"name": "forecast_csv", "description": "Forecast a local CSV."},
        {"name": "forecast_url", "description": "Forecast a CSV URL."},
        {"name": "forecast_dir", "description": "Forecast every CSV inside a folder."},
        {"name": "compare_backends_csv", "description": "Compare multiple backends on a local CSV."},
        {"name": "forecast_stream_csv", "description": "Run a streaming backend."},
        {"name": "run_case", "description": "Run a built-in case."},
        {"name": "build_hosted_site", "description": "Build a static HTML gallery from forecast runs."},
        {"name": "list_examples", "description": "List curated runnable examples."},
        {"name": "demo_examples", "description": "Generate curated example runs and build the examples site."},
        {"name": "build_examples_site", "description": "Build the tutorial-style examples site from generated example runs."},
        {"name": "list_backends", "description": "List registered backends."},
        {"name": "route_backends", "description": "Return candidate backends and routing rationale."},
    ]


def _ok(result: Any) -> dict[str, Any]:
    if hasattr(result, "to_dict"):
        result = result.to_dict()
    return {"ok": True, "tool_version": _TOOL_VERSION, "result": result}


def _error(code: str, message: str, *, help_text: str | None = None, details: dict[str, Any] | None = None, retryable: bool = False) -> dict[str, Any]:
    err = {"kind": _ERROR_KIND, "schema_version": _ERROR_SCHEMA_VERSION, "code": code, "message": message, "schema_ref": _ERROR_SCHEMA, "tool_version": _TOOL_VERSION, "retryable": retryable}
    if help_text:
        err["help"] = help_text
    if details:
        err["details"] = details
    return {"ok": False, "error": err}


def dispatch_tool_call(name: str, args: dict[str, Any]) -> dict[str, Any]:
    try:
        if name == "describe_package":
            return _ok(package_overview(args.get("language", "en")))
        if name == "shoot":
            return _ok(shoot(**args))
        if name == "forecast_dataset":
            return _ok(forecast_dataset(**args))
        if name == "forecast_csv":
            return _ok(forecast_csv(**args))
        if name == "forecast_url":
            return _ok(forecast_url(**args))
        if name == "forecast_dir":
            return _ok(forecast_dir(**args))
        if name == "compare_backends_csv":
            return _ok(compare_backends_csv(**args))
        if name == "forecast_stream_csv":
            return _ok(forecast_stream_csv(**args))
        if name == "run_case":
            return _ok(run_case(**args))
        if name == "build_hosted_site":
            return _ok(build_hosted_site(**args))
        if name == "list_examples":
            return _ok(list_examples())
        if name == "demo_examples":
            return _ok(demo_examples(**args))
        if name == "build_examples_site":
            return _ok(build_examples_site(**args))
        if name == "list_backends":
            return _ok(list_backends(**args))
        if name == "route_backends":
            return _ok(route_backends(**args))
        if name == "list_cases":
            return _ok(list_cases(**args))
        if name == "list_datasets":
            return _ok(list_datasets(**args))
        if name == "list_backend_families":
            return _ok(list_backend_families())
        return _error("TOOL_NOT_FOUND", f"Unknown tool '{name}'.")
    except AgentForecastError as exc:
        return _error(exc.code, exc.message, help_text=exc.help_text, details=exc.details, retryable=exc.retryable)
    except Exception as exc:  # noqa: BLE001
        return _error("INTERNAL_ERROR", str(exc))


def serve_json_tools(*, once_payload: str | None = None) -> int:
    if once_payload is not None:
        request = json.loads(once_payload)
        response = dispatch_tool_call(request["tool"], request.get("args", {}))
        print(json.dumps(response, ensure_ascii=False, indent=2))
        return 0

    hello = {"kind": "agentforecast.tool_server", "tool_version": _TOOL_VERSION, "tools": _tool_catalog()}
    print(json.dumps(hello, ensure_ascii=False))
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        request = json.loads(line)
        response = dispatch_tool_call(request["tool"], request.get("args", {}))
        print(json.dumps(response, ensure_ascii=False), flush=True)
    return 0
