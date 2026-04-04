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
        "SUPPORT_POLICY.md",
        "REVIEWED_SURFACE.md",
        "BENCHMARK_SEMANTICS.md",
        "ARTIFACT_SCHEMA.md",
        "COMMUNITY.md",
        "GOVERNANCE.md",
        "submission/JMLR_SCOPE.md",
        "submission/RELATED_SOFTWARE_TABLE.md",
        "submission/COVER_LETTER_EVIDENCE.md",
        "submission/REPRODUCTION.md",
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

    index_text = (ROOT / "public_gallery" / "site" / "index.html").read_text(encoding="utf-8")
    for needle in ["support-policy/", "benchmarking/", "papers/jmlr-mloss/"]:
        if needle not in index_text:
            raise SystemExit(f"landing page missing link: {needle}")

    print("validated v1.8 assets successfully")


if __name__ == "__main__":
    main()
