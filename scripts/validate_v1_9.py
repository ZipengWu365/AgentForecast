from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agentforecast.backends import list_reviewed_backends  # noqa: E402


def require(path: str) -> Path:
    target = ROOT / path
    if not target.exists():
        raise SystemExit(f"missing: {path}")
    return target


def require_text(path: str, needles: list[str]) -> None:
    text = require(path).read_text(encoding="utf-8")
    for needle in needles:
        if needle not in text:
            raise SystemExit(f"missing text '{needle}' in {path}")


def forbid_text(path: str, needles: list[str]) -> None:
    text = require(path).read_text(encoding="utf-8")
    for needle in needles:
        if needle in text:
            raise SystemExit(f"forbidden text '{needle}' found in {path}")


def main() -> None:
    required = [
        "README.md",
        "README.zh-CN.md",
        "VALIDATION.md",
        "SURFACES.md",
        "SCHEMA_POLICY.md",
        "BENCHMARK_HUB.md",
        "AGENT_SURFACE.md",
        "SUPPORT_POLICY.md",
        "REVIEWED_SURFACE.md",
        "BACKENDS.md",
        "HOSTED_GALLERY_GUIDE.md",
        "COMMUNITY.md",
        "GOVERNANCE.md",
        "ROADMAP.md",
        "submission/JMLR_SCOPE.md",
        "submission/OUTLET_FIT.md",
        "submission/SCIENTIFIC_SOFTWARE_CONTRIBUTION.md",
        "submission/REVIEWER_RESPONSE_MAP.md",
        "submission/SOFTWARE_EVIDENCE_CASE.md",
        "submission/STREAMING_PILOT_APPENDIX.md",
        "submission/RELATED_SOFTWARE_TABLE.md",
        "submission/COVER_LETTER_EVIDENCE.md",
        "submission/COVER_LETTER_DRAFT.md",
        "submission/REPRODUCTION.md",
        "submission/SOFTWARE_PAPER_OUTLINE.md",
        "submission/RESEARCH_BACKLOG.md",
        "public_gallery/site/index.html",
        "public_gallery/site/install/index.html",
        "public_gallery/site/why-agentforecast/index.html",
        "public_gallery/site/surfaces/index.html",
        "public_gallery/site/backends/index.html",
        "public_gallery/site/benchmarking/index.html",
        "public_gallery/site/support-policy/index.html",
        "public_gallery/site/papers/jmlr-mloss/index.html",
        "public_gallery/site/feed.json",
    ]
    for item in required:
        require(item)

    feed = json.loads(require("public_gallery/site/feed.json").read_text(encoding="utf-8"))
    if not feed.get("items"):
        raise SystemExit("gallery feed has no items")

    for path in [
        "README.md",
        "VALIDATION.md",
        "submission/JMLR_SCOPE.md",
        "submission/OUTLET_FIT.md",
        "submission/REPRODUCTION.md",
        "public_gallery/site/index.html",
        "public_gallery/site/papers/jmlr-mloss/index.html",
    ]:
        forbid_text(path, ["v1.7.0", "python -m unittest", "publish_gallery.yml"])

    require_text(
        "README.md",
        [
            "software contribution",
            "not a new forecasting method",
            "stream-eval",
            "doctor",
            "MLForecast",
            "River",
        ],
    )
    require_text(
        "AGENT_SURFACE.md",
        [
            "tool_success.schema.json",
            "tool_error.schema.json",
            "mcp_error.schema.json",
            "METHOD_NOT_FOUND",
            "RESOURCE_NOT_FOUND",
        ],
    )
    require_text(
        "submission/OUTLET_FIT.md",
        [
            "not a Nature Machine Intelligence Article claim",
            "software-first scientific software review",
        ],
    )
    require_text(
        "public_gallery/site/papers/jmlr-mloss/index.html",
        [
            "Streaming pilot appendix",
            "Scope document",
            "Related software table",
            "Reviewer response map",
        ],
    )

    reviewed = [item["backend_id"] for item in list_reviewed_backends()]
    targets = [
        "README.md",
        "SUPPORT_POLICY.md",
        "REVIEWED_SURFACE.md",
        "submission/JMLR_SCOPE.md",
        "VALIDATION.md",
        "public_gallery/site/backends/index.html",
        "public_gallery/site/support-policy/index.html",
    ]
    for backend_id in reviewed:
        for target in targets:
            if backend_id not in require(target).read_text(encoding="utf-8"):
                raise SystemExit(f"reviewed backend '{backend_id}' missing from {target}")

    print("validated v1.9 assets successfully")


if __name__ == "__main__":
    main()
