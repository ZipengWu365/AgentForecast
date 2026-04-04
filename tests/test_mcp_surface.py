from __future__ import annotations

from agentforecast.mcp_server import dispatch_jsonrpc


def test_mcp_resources_include_reviewed_backend_catalog() -> None:
    response = dispatch_jsonrpc({"jsonrpc": "2.0", "id": 1, "method": "resources/list"})
    resources = {item["uri"] for item in response["result"]["resources"]}
    assert "package://agentforecast/reviewed_backends" in resources


def test_mcp_tools_include_backend_capabilities() -> None:
    response = dispatch_jsonrpc({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    names = {item["name"] for item in response["result"]["tools"]}
    assert "backend_capabilities" in names


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
