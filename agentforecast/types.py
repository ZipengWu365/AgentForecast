from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any
from .version import __version__


RESULT_SCHEMA_VERSION = "1.2.0"
ARTIFACT_SCHEMA_VERSION = "1.0.0"
ARTIFACT_MANIFEST_SCHEMA_REF = "package://agentforecast/package_data/schemas/artifact_manifest.schema.json"
TOOL_SUCCESS_SCHEMA_VERSION = "1.0.0"
TOOL_SUCCESS_SCHEMA_REF = "package://agentforecast/package_data/schemas/tool_success.schema.json"
TOOL_ERROR_RESPONSE_SCHEMA_VERSION = "1.0.0"
TOOL_ERROR_RESPONSE_SCHEMA_REF = "package://agentforecast/package_data/schemas/tool_error.schema.json"
TOOL_ERROR_DETAIL_SCHEMA_VERSION = "1.1.0"
TOOL_ERROR_DETAIL_SCHEMA_REF = "package://agentforecast/package_data/schemas/error.schema.json"
MCP_ERROR_SCHEMA_VERSION = "1.0.0"
MCP_ERROR_SCHEMA_REF = "package://agentforecast/package_data/schemas/mcp_error.schema.json"
STREAMING_EVAL_SCHEMA_VERSION = "1.0.0"
STREAMING_EVAL_SCHEMA_REF = "package://agentforecast/package_data/schemas/streaming_eval_result.schema.json"


@dataclass
class ArtifactRef:
    kind: str
    path: str
    media_type: str
    description: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ResolutionInfo:
    requested_backend: str
    resolved_backend: str
    mode: str
    strict_backend: bool
    allow_backend_substitution: bool
    support_tier: str
    dependency_state: dict[str, bool]
    candidate_backends: list[str] = field(default_factory=list)
    routing_reason: str | None = None
    fallback_reason: str | None = None
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RunResult:
    run_type: str
    backend_selected: str
    candidate_backends: list[str]
    feature_spec: dict[str, Any]
    inputs: dict[str, Any]
    summary: dict[str, Any]
    diagnostics: dict[str, Any]
    metrics: dict[str, Any]
    resolution: ResolutionInfo | dict[str, Any] = field(default_factory=dict)
    artifacts: list[ArtifactRef] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    used_live_data: bool = False
    kind: str = "agentforecast.run_result"
    schema_version: str = RESULT_SCHEMA_VERSION
    schema_ref: str = "package://agentforecast/package_data/schemas/run_result.schema.json"
    artifact_schema_version: str = ARTIFACT_SCHEMA_VERSION
    tool_version: str = __version__

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if isinstance(self.resolution, ResolutionInfo):
            payload["resolution"] = self.resolution.to_dict()
        payload["artifacts"] = [artifact.to_dict() for artifact in self.artifacts]
        return payload


@dataclass
class CompareResult:
    run_type: str
    backend_selected: str
    candidate_backends: list[str]
    feature_spec: dict[str, Any]
    inputs: dict[str, Any]
    summary: dict[str, Any]
    diagnostics: dict[str, Any]
    metrics: dict[str, Any]
    leaderboard: list[dict[str, Any]]
    resolution: ResolutionInfo | dict[str, Any] = field(default_factory=dict)
    artifacts: list[ArtifactRef] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    used_live_data: bool = False
    kind: str = "agentforecast.compare_result"
    schema_version: str = RESULT_SCHEMA_VERSION
    schema_ref: str = "package://agentforecast/package_data/schemas/compare_result.schema.json"
    artifact_schema_version: str = ARTIFACT_SCHEMA_VERSION
    tool_version: str = __version__

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if isinstance(self.resolution, ResolutionInfo):
            payload["resolution"] = self.resolution.to_dict()
        payload["artifacts"] = [artifact.to_dict() for artifact in self.artifacts]
        return payload


@dataclass
class DirectoryRunResult:
    inputs: dict[str, Any]
    runs: list[RunResult]
    warnings: list[str] = field(default_factory=list)
    kind: str = "agentforecast.directory_run_result"
    schema_version: str = RESULT_SCHEMA_VERSION
    schema_ref: str = "package://agentforecast/package_data/schemas/directory_run_result.schema.json"
    tool_version: str = __version__

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "schema_version": self.schema_version,
            "schema_ref": self.schema_ref,
            "tool_version": self.tool_version,
            "inputs": self.inputs,
            "runs": [run.to_dict() for run in self.runs],
            "warnings": self.warnings,
        }


@dataclass
class StreamingEvalResult:
    inputs: dict[str, Any]
    summary: dict[str, Any]
    metrics: list[dict[str, Any]]
    diagnostics: dict[str, Any]
    artifacts: list[ArtifactRef] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    kind: str = "agentforecast.streaming_eval_result"
    schema_version: str = STREAMING_EVAL_SCHEMA_VERSION
    schema_ref: str = STREAMING_EVAL_SCHEMA_REF
    tool_version: str = __version__

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "schema_version": self.schema_version,
            "schema_ref": self.schema_ref,
            "tool_version": self.tool_version,
            "inputs": self.inputs,
            "summary": self.summary,
            "metrics": self.metrics,
            "diagnostics": self.diagnostics,
            "artifacts": [artifact.to_dict() for artifact in self.artifacts],
            "warnings": self.warnings,
        }
