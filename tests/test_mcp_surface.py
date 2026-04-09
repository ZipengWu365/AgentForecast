from __future__ import annotations

import json
from pathlib import Path

from agentforecast.mcp_server import dispatch_jsonrpc


ROOT = Path(__file__).resolve().parents[1]


def test_mcp_resources_include_reviewed_backend_catalog() -> None:
    response = dispatch_jsonrpc({"jsonrpc": "2.0", "id": 1, "method": "resources/list"})
    resources = {item["uri"] for item in response["result"]["resources"]}
    assert "package://agentforecast/reviewed_backends" in resources
    assert "package://agentforecast/doctor" in resources


def test_mcp_tools_include_backend_capabilities() -> None:
    response = dispatch_jsonrpc({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    names = {item["name"] for item in response["result"]["tools"]}
    assert "backend_capabilities" in names
    assert "list_examples" in names


def test_mcp_backend_capabilities_call() -> None:
    response = dispatch_jsonrpc(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "backend_capabilities", "arguments": {"backend_id": "stream_ewm"}},
        }
    )
    assert response["result"]["ok"] is True
    assert response["result"]["result"]["supports_online_update"] is True


def test_mcp_unknown_resource_returns_structured_error() -> None:
    response = dispatch_jsonrpc(
        {
            "jsonrpc": "2.0",
            "id": 9,
            "method": "resources/read",
            "params": {"uri": "package://agentforecast/does-not-exist"},
        }
    )
    assert response["error"]["code"] == -32001
    assert response["error"]["data"]["code"] == "RESOURCE_NOT_FOUND"
    assert response["error"]["data"]["details"]["uri"].endswith("does-not-exist")


def test_mcp_unsupported_method_returns_structured_error() -> None:
    response = dispatch_jsonrpc({"jsonrpc": "2.0", "id": 10, "method": "totally/unknown"})
    assert response["error"]["code"] == -32601
    assert response["error"]["data"]["code"] == "METHOD_NOT_FOUND"


def test_mcp_manifest_points_to_contract_schemas() -> None:
    manifest = json.loads((ROOT / "agentforecast" / "package_data" / "manifests" / "mcp_manifest.json").read_text(encoding="utf-8"))
    assert manifest["tool_result_schema_ref"].endswith("tool_success.schema.json")
    assert manifest["tool_error_schema_ref"].endswith("tool_error.schema.json")
    assert manifest["mcp_error_schema_ref"].endswith("mcp_error.schema.json")
