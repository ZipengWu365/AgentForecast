from __future__ import annotations

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def require(path: str) -> None:
    target = ROOT / path
    if not target.exists():
        raise SystemExit(f"missing: {path}")


def main() -> None:
    required = [
        "README.md",
        "README.zh-CN.md",
        "VALIDATION.md",
        "BENCHMARK_HUB.md",
        "AGENT_SURFACE.md",
        "SUPPORT_POLICY.md",
        "REVIEWED_SURFACE.md",
        "BENCHMARK_SEMANTICS.md",
        "ARTIFACT_SCHEMA.md",
        "COMMUNITY.md",
        "GOVERNANCE.md",
        "ROADMAP.md",
        "submission/JMLR_SCOPE.md",
        "submission/OUTLET_FIT.md",
        "submission/SCIENTIFIC_SOFTWARE_CONTRIBUTION.md",
        "submission/REVIEWER_RESPONSE_MAP.md",
        "submission/SOFTWARE_EVIDENCE_CASE.md",
        "submission/RELATED_SOFTWARE_TABLE.md",
        "submission/COVER_LETTER_EVIDENCE.md",
        "submission/REPRODUCTION.md",
        "submission/RESEARCH_BACKLOG.md",
        "public_gallery/site/index.html",
        "public_gallery/site/gallery/index.html",
        "public_gallery/site/install/index.html",
        "public_gallery/site/why-agentforecast/index.html",
        "public_gallery/site/backends/index.html",
        "public_gallery/site/benchmarking/index.html",
        "public_gallery/site/support-policy/index.html",
        "public_gallery/site/papers/jmlr-mloss/index.html",
        "public_gallery/site/feed.json",
    ]
    for item in required:
        require(item)

    feed = json.loads((ROOT / "public_gallery" / "site" / "feed.json").read_text(encoding="utf-8"))
    if not feed.get("items"):
        raise SystemExit("gallery feed has no items")

    text_targets = [
        ROOT / "README.md",
        ROOT / "VALIDATION.md",
        ROOT / "AGENT_SURFACE.md",
        ROOT / "submission" / "JMLR_SCOPE.md",
        ROOT / "submission" / "OUTLET_FIT.md",
        ROOT / "submission" / "REPRODUCTION.md",
        ROOT / "public_gallery" / "site" / "index.html",
        ROOT / "public_gallery" / "site" / "papers" / "jmlr-mloss" / "index.html",
    ]
    prohibited = ["v1.7.0", "python -m unittest", "publish_gallery.yml"]
    for target in text_targets:
        text = target.read_text(encoding="utf-8")
        for needle in prohibited:
            if needle in text:
                raise SystemExit(f"prohibited text '{needle}' found in {target.relative_to(ROOT)}")

    readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
    for needle in [
        "software contribution",
        "not a new forecasting method",
        "BENCHMARK_HUB.md",
        "submission/OUTLET_FIT.md",
    ]:
        if needle not in readme_text:
            raise SystemExit(f"README.md missing required phrase: {needle}")

    agent_text = (ROOT / "AGENT_SURFACE.md").read_text(encoding="utf-8")
    for needle in [
        "tool_success.schema.json",
        "tool_error.schema.json",
        "mcp_error.schema.json",
        "METHOD_NOT_FOUND",
    ]:
        if needle not in agent_text:
            raise SystemExit(f"AGENT_SURFACE.md missing required phrase: {needle}")

    index_text = (ROOT / "public_gallery" / "site" / "index.html").read_text(encoding="utf-8")
    for needle in ["support-policy/", "benchmarking/", "papers/jmlr-mloss/"]:
        if needle not in index_text:
            raise SystemExit(f"landing page missing link: {needle}")

    paper_text = (ROOT / "public_gallery" / "site" / "papers" / "jmlr-mloss" / "index.html").read_text(encoding="utf-8")
    for needle in ["Outlet-fit memo", "Scientific software memo", "Benchmark hub", "Validation evidence"]:
        if needle not in paper_text:
            raise SystemExit(f"paper page missing link or phrase: {needle}")

    print("validated v1.8 assets successfully")


if __name__ == "__main__":
    main()
