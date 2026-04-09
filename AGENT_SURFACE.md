# Agent / Tool / MCP Surface

This file documents the stable contract and governance rules for agent-facing consumption.

## Stable tool success envelope

Every successful tool response contains:

- `schema_version`
- `schema_ref`
- `tool_version`
- `warnings`
- `resolution`
- `artifacts`
- `result`

Schema reference:

- `package://agentforecast/package_data/schemas/tool_success.schema.json`

## Stable tool error envelope

Every tool error response contains:

- top-level envelope fields matching the success envelope shape where applicable
- structured `error.kind`
- structured `error.code`
- human-readable `error.message`
- optional `error.help`
- optional `error.details`
- `error.retryable`

Schema references:

- `package://agentforecast/package_data/schemas/tool_error.schema.json`
- `package://agentforecast/package_data/schemas/error.schema.json`

## Stable MCP protocol errors

The MCP surface preserves JSON-RPC 2.0 envelopes. Protocol failures return structured `error.data` with:

- `schema_version`
- `schema_ref`
- `tool_version`
- `code`
- `retryable`
- optional `details`

Schema reference:

- `package://agentforecast/package_data/schemas/mcp_error.schema.json`

## Malformed input handling

- unknown tool: `TOOL_NOT_FOUND`
- missing required tool args: `INVALID_ARGUMENTS`
- unsupported JSON-RPC method: `METHOD_NOT_FOUND`
- unknown resource URI: `RESOURCE_NOT_FOUND`
- benchmark or backend failures: package-specific structured error codes

## MCP compatibility

Supported methods:

- `initialize`
- `tools/list`
- `tools/call`
- `resources/list`
- `resources/read`

Stable resource URIs include:

- `package://agentforecast/overview`
- `package://agentforecast/reviewed_backends`
- `package://agentforecast/doctor`

## Warnings taxonomy

- `dependency`
- `fallback`
- `experimental`
- `input`
- `provenance`

## Discoverability

`doctor` is the reviewed operations entrypoint for CLI, tool, and MCP consumers. It reports:

- installed extras
- reviewed workflows available
- missing promoted backends
- recommended next command
- docs and support links

See also: [SCHEMA_POLICY.md](SCHEMA_POLICY.md)
