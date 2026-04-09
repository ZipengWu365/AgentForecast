from __future__ import annotations

import json
from pathlib import Path

from agentforecast.tool_server import dispatch_tool_call
from agentforecast.types import TOOL_ERROR_RESPONSE_SCHEMA_REF, TOOL_SUCCESS_SCHEMA_REF


ROOT = Path(__file__).resolve().parents[1]


def test_tool_server_error_shape() -> None:
    payload = dispatch_tool_call("nope", {})
    assert payload["ok"] is False
    assert payload["schema_ref"] == TOOL_ERROR_RESPONSE_SCHEMA_REF
    assert payload["kind"] == "agentforecast.tool_response"
    assert payload["error"]["code"] == "TOOL_NOT_FOUND"
    assert "schema_ref" in payload["error"]
    assert "retryable" in payload["error"]
    assert payload["warnings"] == []
    assert payload["resolution"] is None
    assert payload["artifacts"] == []


def test_tool_server_lists_reviewed_backends() -> None:
    payload = dispatch_tool_call("list_reviewed_backends", {})
    backend_ids = {item["backend_id"] for item in payload["result"]}
    assert payload["ok"] is True
    assert payload["schema_ref"] == TOOL_SUCCESS_SCHEMA_REF
    assert payload["kind"] == "agentforecast.tool_response"
    assert payload["warnings"] == []
    assert payload["resolution"] is None
    assert payload["artifacts"] == []
    assert "stats_ets" in backend_ids
    assert "mlforecast_linear" in backend_ids
    assert "river_linear" in backend_ids
    assert "river_snarimax" in backend_ids


def test_tool_server_backend_capabilities() -> None:
    payload = dispatch_tool_call("backend_capabilities", {"backend_id": "ml_ridge"})
    assert payload["ok"] is True
    assert payload["result"]["tier"] == "reviewed"
    assert payload["result"]["supports_exogenous"] is True


def test_tool_server_reports_invalid_arguments() -> None:
    payload = dispatch_tool_call("backend_capabilities", {})
    assert payload["ok"] is False
    assert payload["error"]["code"] == "INVALID_ARGUMENTS"
    assert payload["error"]["details"]["missing_argument"] == "backend_id"


def test_tool_manifest_points_to_contract_schemas() -> None:
    manifest = json.loads((ROOT / "agentforecast" / "package_data" / "manifests" / "tool_manifest.json").read_text(encoding="utf-8"))
    assert manifest["success_schema_ref"] == TOOL_SUCCESS_SCHEMA_REF
    assert manifest["error_schema_ref"] == TOOL_ERROR_RESPONSE_SCHEMA_REF
    tool_names = {item["name"] for item in manifest["tools"]}
    assert "doctor" in tool_names
    assert "list_examples" in tool_names
    assert "route_backends" in tool_names
