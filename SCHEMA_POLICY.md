# Schema Policy

## Stable schema references

- `tool_success.schema.json`
- `tool_error.schema.json`
- `error.schema.json`
- `mcp_error.schema.json`
- `artifact_manifest.schema.json`
- `streaming_eval_result.schema.json`

## Versioning rule

- additive compatible fields may keep the same `schema_version`
- breaking envelope or required-field changes require a new `schema_version`
- manifest files must be updated when schema references or guarantees change

## Deprecation rule

- deprecated fields remain readable for at least one reviewed release after notice
- new docs must mark deprecated fields explicitly
- removed fields require a version bump and release-note disclosure

## Consumer rule

Tool and MCP consumers should key off:

- `schema_version`
- `schema_ref`
- `tool_version`

not off undocumented field presence or response ordering.
