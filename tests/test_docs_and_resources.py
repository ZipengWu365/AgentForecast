from __future__ import annotations

from pathlib import Path

from agentforecast import build_hosted_site, forecast_csv
from agentforecast.public_examples import public_example_path
from agentforecast.resources import api_catalog, describe_package, package_overview


def test_resources_expose_doctor_and_streaming_pilot() -> None:
    catalog_names = {item["name"] for item in api_catalog()}
    overview = package_overview("en")
    description = describe_package("en")

    assert "doctor" in catalog_names
    assert "stream_eval" in catalog_names
    assert "doctor" in overview
    assert "streaming_pilot" in overview
    assert "mlforecast_linear" in description["reviewed_backends"]
    assert "river_linear" in description["reviewed_backends"]
    assert "river_snarimax" in description["reviewed_backends"]


def test_build_hosted_site_generates_review_pages(tmp_path: Path) -> None:
    runs_root = tmp_path / "runs"
    site_dir = tmp_path / "site"
    forecast_csv(
        public_example_path("monthly-car-sales"),
        backend="naive",
        horizon=12,
        outdir=runs_root,
        strict_backend=True,
        mode="benchmark",
    )

    payload = build_hosted_site(runs_root, site_dir)
    index_text = (site_dir / "index.html").read_text(encoding="utf-8")
    paper_text = (site_dir / "papers" / "jmlr-mloss" / "index.html").read_text(encoding="utf-8")

    assert payload["entry_count"] == 1
    assert (site_dir / "install" / "index.html").exists()
    assert (site_dir / "surfaces" / "index.html").exists()
    assert (site_dir / "support-policy" / "index.html").exists()
    assert "software-first submission" in index_text
    assert "not a new forecasting method" in index_text
    assert "streaming annex" in paper_text.lower()
    assert "Scope document" in paper_text
