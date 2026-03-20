from __future__ import annotations

import json
import sys
from typing import Any

from .benchmark_hub import list_external_benchmarks
from .datasets import list_datasets
from .live import list_cases
from .backends import list_backends, list_backend_families
from .resources import package_overview
from .tool_server import dispatch_tool_call
from .version import __version__


_RESOURCES = {
    "package://agentforecast/overview": lambda: package_overview("en"),
    "package://agentforecast/benchmark_api": lambda: {
        "headline": "Benchmark-first API",
        "symbols": ["OnlineForecaster", "forecast_benchmark_dataframe", "list_feature_presets"],
        "notes": "Use strict_mode=True, horizons=[...], lookback/max_history, and mode=recursive|direct for reproducible low-level benchmarking.",
    },
    "package://agentforecast/backends": lambda: list_backends(),
    "package://agentforecast/backend_families": lambda: list_backend_families(),
    "package://agentforecast/datasets": lambda: list_datasets("en"),
    "package://agentforecast/cases": lambda: list_cases("en"),
    "package://agentforecast/benchmark_hub": lambda: list_external_benchmarks(),
}


def _tools_list() -> dict[str, Any]:
    return {
        "tools": [
            {"name": "describe_package", "description": "Describe the package and safest quickstart.", "inputSchema": {"type": "object", "properties": {"language": {"type": "string"}}}},
            {
                "name": "forecast_benchmark_dataframe",
                "description": "Run the benchmark-first low-level dataframe forecast API.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "frame": {"type": "array", "items": {"type": "object"}},
                        "backend": {"type": "string"},
                        "horizon": {"type": "integer"},
                        "horizons": {"type": "array", "items": {"type": "integer"}},
                        "mode": {"type": "string", "enum": ["recursive", "direct"]},
                        "date_col": {"type": "string"},
                        "value_col": {"type": "string"},
                        "lookback": {"type": "integer"},
                        "max_history": {"type": "integer"},
                        "strict_mode": {"type": "boolean"},
                        "feature_preset": {"type": "string"}
                    },
                    "required": ["frame"]
                }
            },
            {"name": "list_feature_presets", "description": "List benchmark feature presets.", "inputSchema": {"type": "object", "properties": {}}},
            {"name": "shoot", "description": "Camera mode for datasets, cases, CSV files, directories, or CSV URLs.", "inputSchema": {"type": "object", "properties": {"target": {"type": "string"}, "backend": {"type": "string"}, "strategy": {"type": "string"}, "horizon": {"type": "integer"}, "outdir": {"type": "string"}}, "required": ["target"]}},
            {"name": "forecast_dataset", "description": "Forecast a bundled dataset.", "inputSchema": {"type": "object", "properties": {"dataset_id": {"type": "string"}, "horizon": {"type": "integer"}, "backend": {"type": "string"}, "strategy": {"type": "string"}, "outdir": {"type": "string"}}, "required": ["dataset_id"]}},
            {"name": "forecast_csv", "description": "Forecast a local CSV path.", "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}, "date_col": {"type": "string"}, "value_col": {"type": "string"}, "horizon": {"type": "integer"}, "backend": {"type": "string"}, "strategy": {"type": "string"}, "outdir": {"type": "string"}}, "required": ["path"]}},
            {"name": "compare_backends_csv", "description": "Compare multiple backends on one CSV.", "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}, "backends": {"type": "array", "items": {"type": "string"}}, "horizon": {"type": "integer"}, "outdir": {"type": "string"}}, "required": ["path", "backends"]}},
            {"name": "forecast_stream_csv", "description": "Run a streaming backend and export drift diagnostics.", "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}, "backend": {"type": "string"}, "horizon": {"type": "integer"}, "outdir": {"type": "string"}}, "required": ["path"]}},
            {"name": "run_case", "description": "Run a built-in case.", "inputSchema": {"type": "object", "properties": {"case_id": {"type": "string"}, "outdir": {"type": "string"}, "backend": {"type": "string"}, "strategy": {"type": "string"}}, "required": ["case_id"]}},
            {"name": "build_hosted_site", "description": "Build a static HTML gallery from run directories.", "inputSchema": {"type": "object", "properties": {"runs_root": {"type": "string"}, "site_dir": {"type": "string"}}, "required": ["runs_root", "site_dir"]}},
        ]
    }


def _resources_list() -> dict[str, Any]:
    return {"resources": [{"uri": uri, "name": uri.split('/')[-1]} for uri in sorted(_RESOURCES)]}


def _resources_read(uri: str) -> dict[str, Any]:
    if uri not in _RESOURCES:
        return {"contents": [{"uri": uri, "mimeType": "application/json", "text": json.dumps({"error": {"code": "RESOURCE_NOT_FOUND", "message": uri}}, ensure_ascii=False)}]}
    payload = _RESOURCES[uri]()
    return {"contents": [{"uri": uri, "mimeType": "application/json", "text": json.dumps(payload, ensure_ascii=False)}]}


def dispatch_jsonrpc(request: dict[str, Any]) -> dict[str, Any]:
    method = request.get("method")
    req_id = request.get("id")
    params = request.get("params", {})
    if method == "initialize":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"serverInfo": {"name": "agentforecast-mcp", "version": __version__}, "capabilities": {"tools": {}, "resources": {}}}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": _tools_list()}
    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        result = dispatch_tool_call(tool_name, arguments)
        return {"jsonrpc": "2.0", "id": req_id, "result": result}
    if method == "resources/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": _resources_list()}
    if method == "resources/read":
        return {"jsonrpc": "2.0", "id": req_id, "result": _resources_read(params.get("uri", ""))}
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method '{method}' not found."}}


def serve_mcp(*, once_payload: str | None = None) -> int:
    if once_payload is not None:
        request = json.loads(once_payload)
        print(json.dumps(dispatch_jsonrpc(request), ensure_ascii=False, indent=2))
        return 0
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        request = json.loads(line)
        response = dispatch_jsonrpc(request)
        print(json.dumps(response, ensure_ascii=False), flush=True)
    return 0
