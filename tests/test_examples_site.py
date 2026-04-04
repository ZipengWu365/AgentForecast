from __future__ import annotations

from pathlib import Path

from agentforecast import build_examples_site, demo_examples, list_examples


def test_list_examples_exposes_curated_ids() -> None:
    example_ids = {item["example_id"] for item in list_examples()}
    assert "first-forecast-pack" in example_ids
    assert "time-series-as-regression" in example_ids


def test_demo_examples_builds_site(tmp_path: Path) -> None:
    runs = tmp_path / "generated"
    site = tmp_path / "site"
    payload = demo_examples(runs, site, example_ids=["first-forecast-pack", "time-series-as-regression"])
    rebuilt = build_examples_site(runs, site)

    assert payload["example_count"] == 2
    assert rebuilt["entry_count"] == 2
    assert (site / "index.html").exists()
    assert (site / "examples" / "first-forecast-pack.html").exists()
