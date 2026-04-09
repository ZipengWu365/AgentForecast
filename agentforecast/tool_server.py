from __future__ import annotations

import json
import sys
from typing import Any

from .backends import backend_capabilities, list_backends, list_reviewed_backends, route_backends
from .doctor import doctor
from .errors import AgentForecastError
from .examples_hub import build_examples_site, demo_examples, list_examples
from .hosted import build_hosted_site
from .live import run_case
from .local import (
    compare_backends_csv,
    forecast_csv,
    forecast_dataset,
    forecast_dir,
    forecast_stream_csv,
    forecast_url,
    shoot,
)
from .resources import package_overview
from .types import (
    TOOL_ERROR_DETAIL_SCHEMA_REF,
    TOOL_ERROR_DETAIL_SCHEMA_VERSION,
    TOOL_ERROR_RESPONSE_SCHEMA_REF,
    TOOL_ERROR_RESPONSE_SCHEMA_VERSION,
    TOOL_SUCCESS_SCHEMA_REF,
    TOOL_SUCCESS_SCHEMA_VERSION,
)
from .version import __version__


_TOOL_VERSION = __version__
_TOOL_RESPONSE_KIND = "agentforecast.tool_response"
_TOOL_ERROR_KIND = "agentforecast.error"

_TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "name": "doctor",
        "description": "Inspect installed extras, reviewed workflows, promoted backend availability, and the next recommended command.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "describe_package",
        "description": "Describe the package, public boundaries, and safest quickstart.",
        "input_schema": {"type": "object", "properties": {"language": {"type": "string"}}},
    },
    {
        "name": "shoot",
        "description": "Camera mode for datasets, cases, local CSV, directories, or CSV URLs.",
        "input_schema": {
            "type": "object",
            "properties": {
                "target": {"type": "string"},
                "backend": {"type": "string"},
                "strategy": {"type": "string"},
                "horizon": {"type": "integer"},
                "outdir": {"type": "string"},
            },
            "required": ["target"],
        },
    },
    {
        "name": "forecast_dataset",
        "description": "Forecast a bundled dataset.",
        "input_schema": {
            "type": "object",
            "properties": {
                "dataset_id": {"type": "string"},
                "horizon": {"type": "integer"},
                "backend": {"type": "string"},
                "strategy": {"type": "string"},
                "outdir": {"type": "string"},
            },
            "required": ["dataset_id"],
        },
    },
    {
        "name": "forecast_csv",
        "description": "Forecast a local CSV.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "date_col": {"type": "string"},
                "value_col": {"type": "string"},
                "horizon": {"type": "integer"},
                "backend": {"type": "string"},
                "strategy": {"type": "string"},
                "outdir": {"type": "string"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "forecast_url",
        "description": "Forecast a CSV URL.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string"},
                "horizon": {"type": "integer"},
                "backend": {"type": "string"},
                "strategy": {"type": "string"},
                "outdir": {"type": "string"},
            },
            "required": ["url"],
        },
    },
    {
        "name": "forecast_dir",
        "description": "Forecast every CSV inside a folder.",
        "input_schema": {
            "type": "object",
            "properties": {
                "directory": {"type": "string"},
                "horizon": {"type": "integer"},
                "backend": {"type": "string"},
                "strategy": {"type": "string"},
                "outdir": {"type": "string"},
            },
            "required": ["directory"],
        },
    },
    {
        "name": "compare_backends_csv",
        "description": "Compare multiple backends on a local CSV.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "backends": {"type": "array", "items": {"type": "string"}},
                "horizon": {"type": "integer"},
                "outdir": {"type": "string"},
            },
            "required": ["path", "backends"],
        },
    },
    {
        "name": "forecast_stream_csv",
        "description": "Run a streaming backend.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "backend": {"type": "string"},
                "horizon": {"type": "integer"},
                "outdir": {"type": "string"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "run_case",
        "description": "Run a built-in case.",
        "input_schema": {
            "type": "object",
            "properties": {
                "case_id": {"type": "string"},
                "outdir": {"type": "string"},
                "backend": {"type": "string"},
                "strategy": {"type": "string"},
            },
            "required": ["case_id"],
        },
    },
    {
        "name": "build_hosted_site",
        "description": "Build a static HTML gallery from forecast runs.",
        "input_schema": {
            "type": "object",
            "properties": {
                "runs_root": {"type": "string"},
                "site_dir": {"type": "string"},
            },
            "required": ["runs_root", "site_dir"],
        },
    },
    {
        "name": "list_examples",
        "description": "List curated runnable examples.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "demo_examples",
        "description": "Generate curated example runs and build the examples site.",
        "input_schema": {
            "type": "object",
            "properties": {
                "outdir": {"type": "string"},
                "site_dir": {"type": "string"},
                "examples": {"type": "array", "items": {"type": "string"}},
            },
        },
    },
    {
        "name": "build_examples_site",
        "description": "Build the tutorial-style examples site from generated example runs.",
        "input_schema": {
            "type": "object",
            "properties": {
                "runs_root": {"type": "string"},
                "site_dir": {"type": "string"},
            },
            "required": ["runs_root", "site_dir"],
        },
    },
    {
        "name": "list_backends",
        "description": "List registered backends.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "list_reviewed_backends",
        "description": "List the reviewed backend surface for the paper release.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "backend_capabilities",
        "description": "Describe support tier, dependencies, and capabilities for one backend.",
        "input_schema": {
            "type": "object",
            "properties": {"backend_id": {"type": "string"}},
            "required": ["backend_id"],
        },
    },
    {
        "name": "route_backends",
        "description": "Return candidate backends and routing rationale.",
        "input_schema": {
            "type": "object",
            "properties": {
                "history_len": {"type": "integer"},
                "horizon": {"type": "integer"},
                "strategy": {"type": "string"},
                "exogenous_cols": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["history_len", "horizon"],
        },
    },
]


def tool_catalog() -> list[dict[str, Any]]:
    return [
        {
            **item,
            "success_schema_ref": TOOL_SUCCESS_SCHEMA_REF,
            "error_schema_ref": TOOL_ERROR_RESPONSE_SCHEMA_REF,
        }
        for item in _TOOL_DEFINITIONS
    ]


def _success_contract_fields(result: Any) -> tuple[list[str], Any, list[Any]]:
    if isinstance(result, dict):
        warnings = result.get("warnings", [])
        artifacts = result.get("artifacts", [])
        resolution = result.get("resolution")
        return list(warnings) if isinstance(warnings, list) else [], resolution, list(artifacts) if isinstance(artifacts, list) else []
    return [], None, []


def _ok(result: Any) -> dict[str, Any]:
    if hasattr(result, "to_dict"):
        result = result.to_dict()
    warnings, resolution, artifacts = _success_contract_fields(result)
    return {
        "kind": _TOOL_RESPONSE_KIND,
        "ok": True,
        "schema_version": TOOL_SUCCESS_SCHEMA_VERSION,
        "schema_ref": TOOL_SUCCESS_SCHEMA_REF,
        "tool_version": _TOOL_VERSION,
        "warnings": warnings,
        "resolution": resolution,
        "artifacts": artifacts,
        "result": result,
    }


def _error(
    code: str,
    message: str,
    *,
    help_text: str | None = None,
    details: dict[str, Any] | None = None,
    retryable: bool = False,
) -> dict[str, Any]:
    err = {
        "kind": _TOOL_ERROR_KIND,
        "schema_version": TOOL_ERROR_DETAIL_SCHEMA_VERSION,
        "schema_ref": TOOL_ERROR_DETAIL_SCHEMA_REF,
        "tool_version": _TOOL_VERSION,
        "code": code,
        "message": message,
        "retryable": retryable,
    }
    if help_text:
        err["help"] = help_text
    if details:
        err["details"] = details
    return {
        "kind": _TOOL_RESPONSE_KIND,
        "ok": False,
        "schema_version": TOOL_ERROR_RESPONSE_SCHEMA_VERSION,
        "schema_ref": TOOL_ERROR_RESPONSE_SCHEMA_REF,
        "tool_version": _TOOL_VERSION,
        "warnings": [],
        "resolution": None,
        "artifacts": [],
        "error": err,
    }


def dispatch_tool_call(name: str, args: dict[str, Any]) -> dict[str, Any]:
    try:
        if name == "doctor":
            return _ok(doctor())
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
        if name == "list_reviewed_backends":
            return _ok(list_reviewed_backends())
        if name == "backend_capabilities":
            return _ok(backend_capabilities(args["backend_id"]))
        if name == "route_backends":
            return _ok(route_backends(**args))
        return _error("TOOL_NOT_FOUND", f"Unknown tool '{name}'.")
    except KeyError as exc:
        missing = exc.args[0]
        return _error(
            "INVALID_ARGUMENTS",
            f"Missing required argument '{missing}'.",
            details={"missing_argument": str(missing)},
        )
    except TypeError as exc:
        return _error("INVALID_ARGUMENTS", str(exc))
    except AgentForecastError as exc:
        return _error(
            exc.code,
            exc.message,
            help_text=exc.help_text,
            details=exc.details,
            retryable=exc.retryable,
        )
    except Exception as exc:  # noqa: BLE001
        return _error("INTERNAL_ERROR", str(exc))


def serve_json_tools(*, once_payload: str | None = None) -> int:
    if once_payload is not None:
        request = json.loads(once_payload)
        response = dispatch_tool_call(request["tool"], request.get("args", {}))
        print(json.dumps(response, ensure_ascii=False, indent=2))
        return 0

    hello = {
        "kind": "agentforecast.tool_server",
        "tool_version": _TOOL_VERSION,
        "success_schema_ref": TOOL_SUCCESS_SCHEMA_REF,
        "error_schema_ref": TOOL_ERROR_RESPONSE_SCHEMA_REF,
        "tools": tool_catalog(),
    }
    print(json.dumps(hello, ensure_ascii=False))
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        request = json.loads(line)
        response = dispatch_tool_call(request["tool"], request.get("args", {}))
        print(json.dumps(response, ensure_ascii=False), flush=True)
    return 0
