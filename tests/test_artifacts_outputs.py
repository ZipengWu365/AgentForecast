from __future__ import annotations

import json
from pathlib import Path

from agentforecast import build_hosted_site, forecast_dataset, shoot


def test_artifact_manifest_contains_contract_fields(tmp_path: Path) -> None:
    forecast_dataset("sales", outdir=tmp_path)
    manifest_path = tmp_path / "sales" / "meta" / "artifact_manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert payload["kind"] == "agentforecast.artifact_manifest"
    assert payload["schema_ref"].endswith("artifact_manifest.schema.json")
    assert payload["resolution"]["resolved_backend"]
    assert any(item["kind"] == "metadata_json" for item in payload["artifacts"])


def test_build_hosted_site_creates_docs_and_gallery_pages(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    site = tmp_path / "site"
    shoot("sales", outdir=runs)
    manifest = build_hosted_site(runs, site)
    index_text = (site / "index.html").read_text(encoding="utf-8")

    assert manifest["entry_count"] == 1
    assert (site / "install" / "index.html").exists()
    assert (site / "benchmarking" / "index.html").exists()
    assert (site / "support-policy" / "index.html").exists()
    assert (site / "papers" / "jmlr-mloss" / "index.html").exists()
    assert "support-policy/" in index_text
    assert "papers/jmlr-mloss/" in index_text
