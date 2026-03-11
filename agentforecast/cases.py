
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class CaseSpec:
    case_id: str
    title_en: str
    title_zh: str
    dataset_id: str
    default_horizon: int
    default_strategy: str
    description_en: str
    description_zh: str

    def to_dict(self, language: str = "en") -> dict[str, Any]:
        zh = language.lower().startswith("zh")
        return {
            "case_id": self.case_id,
            "title": self.title_zh if zh else self.title_en,
            "dataset_id": self.dataset_id,
            "default_horizon": self.default_horizon,
            "default_strategy": self.default_strategy,
            "description": self.description_zh if zh else self.description_en,
        }


_CASES = [
    CaseSpec("github-breakout-radar", "GitHub Breakout Radar", "GitHub 爆火雷达", "github-breakout", 30, "accurate", "Forecast which repository is still accelerating.", "预测仓库是否仍在持续加速增长。"),
    CaseSpec("gold-forecaster-arena", "Gold Forecaster Arena", "黄金预测擂台", "gold", 30, "accurate", "Compare classical, tabular, and streaming backends on a gold-like series.", "在黄金风格序列上比较 classical、tabular 和 streaming 后端。"),
    CaseSpec("air-quality-smoke-watch", "Wildfire Smoke Morning Brief", "野火烟尘晨报", "air-quality-smoke", 7, "accurate", "Generate a public-facing air-risk forecast pack.", "生成面向公众的空气风险预测包。"),
    CaseSpec("icu-bed-stress-watch", "ICU Bed Stress Watch", "ICU 床位压力监测", "icu-bed-stress", 14, "streaming", "Use batch plus streaming backends for hospital pressure monitoring.", "用 batch 与 streaming 后端监测医院床位压力。"),
    CaseSpec("beamline-drift-watch", "Beamline Drift Watch", "束线漂移监测", "beamline-drift", 14, "streaming", "Track instrument drift and publish a compact diagnostic pack.", "跟踪仪器漂移并发布紧凑诊断包。"),
    CaseSpec("transit-demand-shock-watch", "Transit Demand Shock Monitor", "交通需求冲击监测", "transit-demand-shock", 14, "accurate", "Turn ridership volatility into a publishable operational brief.", "把客流波动变成可发布的运营简报。"),
    CaseSpec("grid-heatwave-stress-watch", "Grid Heatwave Stress Watch", "电网热浪压力监测", "grid-heatwave-stress", 14, "accurate", "Turn heat-driven demand stress into a public utility briefing.", "把热浪驱动的负荷压力变成公用事业简报。"),
    CaseSpec("river-flood-risk-watch", "River Flood Risk Watch", "河流水位风险监测", "river-flood-risk", 10, "streaming", "Use streaming updates for rainfall-driven flood-risk monitoring.", "用 streaming 更新监测降雨驱动的洪水风险。"),
    CaseSpec("outpatient-no-show-watch", "Outpatient No-Show Watch", "门诊爽约率监测", "outpatient-no-show", 14, "accurate", "Forecast scheduling stress from changing no-show patterns.", "根据变化的爽约模式预测排班压力。"),
]
