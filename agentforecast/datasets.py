
from __future__ import annotations

from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any
import shutil


@dataclass
class DatasetSpec:
    dataset_id: str
    file_name: str
    title_en: str
    title_zh: str
    description_en: str
    description_zh: str
    domain: str
    provenance_en: str
    provenance_zh: str
    date_col: str = "ds"
    value_col: str = "y"
    series_kind: str = "auto"
    default_horizon: int = 14

    def to_dict(self, language: str = "en") -> dict[str, Any]:
        zh = language.lower().startswith("zh")
        return {
            "dataset_id": self.dataset_id,
            "file_name": self.file_name,
            "title": self.title_zh if zh else self.title_en,
            "description": self.description_zh if zh else self.description_en,
            "domain": self.domain,
            "provenance": self.provenance_zh if zh else self.provenance_en,
            "date_col": self.date_col,
            "value_col": self.value_col,
            "series_kind": self.series_kind,
            "default_horizon": self.default_horizon,
        }


_DATASETS = [
    DatasetSpec("sales", "sales.csv", "Daily retail sales", "日频零售销量", "A simple daily sales series for first-run demos.", "用于首次上手的简单日频销量序列。", "retail", "Bundled synthetic demo dataset packaged with agentforecast.", "随 agentforecast 打包的合成演示数据集。", default_horizon=14),
    DatasetSpec("gold", "gold.csv", "Gold price watch", "黄金价格观察", "Synthetic gold-like market series with trend and stress swings.", "带趋势和风险波动的拟合黄金价格序列。", "markets", "Bundled demo snapshot inspired by market stress series.", "受市场压力序列启发的打包演示快照。", series_kind="price", default_horizon=30),
    DatasetSpec("gold-exogenous", "gold_exogenous.csv", "Gold with exogenous signals", "带外生变量的黄金序列", "Gold-like target with demo DXY, VIX, and 10Y-yield style exogenous columns.", "带 DXY、VIX 和 10Y 利率风格外生变量的黄金序列。", "markets", "Bundled synthetic exogenous-feature demo dataset.", "带外生特征的合成演示数据集。", series_kind="price", default_horizon=30),
    DatasetSpec("github-breakout", "github_breakout.csv", "GitHub breakout radar", "GitHub 爆火雷达", "Cumulative stars for a fast-growing open-source repository.", "快速增长开源仓库的累计 star 序列。", "open-source", "Bundled cumulative demo snapshot inspired by stargazer histories.", "受 stargazer 历史启发的累计型演示快照。", series_kind="cumulative", default_horizon=30),
    DatasetSpec("air-quality-smoke", "air_quality_smoke.csv", "Air quality smoke watch", "空气质量烟尘观察", "AQI-style public-risk series for smoke events.", "用于烟尘事件的 AQI 风格公共风险序列。", "climate", "Bundled synthetic public-risk demo series.", "打包的公共风险合成演示序列。", default_horizon=7),
    DatasetSpec("icu-bed-stress", "icu_bed_stress.csv", "ICU bed stress watch", "ICU 床位压力观察", "Hospital pressure style occupancy series.", "医院床位占用压力风格序列。", "medicine", "Bundled synthetic hospital-ops demo series.", "打包的医院运营合成演示序列。", default_horizon=14),
    DatasetSpec("beamline-drift", "beamline_drift.csv", "Beamline drift watch", "束线漂移观察", "Instrument drift monitoring series for physics or engineering.", "用于物理或工程场景的仪器漂移监测序列。", "physics", "Bundled synthetic instrument-monitoring demo series.", "打包的仪器监测合成演示序列。", default_horizon=14),
    DatasetSpec("transit-demand-shock", "transit_demand_shock.csv", "Transit demand shock monitor", "交通需求冲击监测", "Ridership-like series with event-driven shocks.", "带事件冲击的客流需求风格序列。", "social-science", "Bundled synthetic operations-volatility demo series.", "打包的运营波动合成演示序列。", default_horizon=14),
    DatasetSpec("grid-heatwave-stress", "grid_heatwave_stress.csv", "Grid heatwave stress watch", "电网热浪压力监测", "Power-demand style series with heatwave stress and recovery.", "带热浪冲击和恢复过程的电网负荷风格序列。", "engineering", "Bundled synthetic grid-stress demo series.", "打包的电网压力合成演示序列。", default_horizon=14),
    DatasetSpec("river-flood-risk", "river_flood_risk.csv", "River flood risk watch", "河流水位风险监测", "Hydrology-style risk series with rainfall-driven surges.", "带降雨冲击的水文风险风格序列。", "climate", "Bundled synthetic hydrology demo series.", "打包的水文合成演示序列。", default_horizon=10),
    DatasetSpec("outpatient-no-show", "outpatient_no_show.csv", "Outpatient no-show watch", "门诊爽约率监测", "Clinic scheduling stress series with calendar effects.", "带日历效应的门诊排班压力序列。", "medicine", "Bundled synthetic healthcare-ops demo series.", "打包的医疗运营合成演示序列。", default_horizon=14),
]


def list_dataset_specs() -> list[DatasetSpec]:
    return list(_DATASETS)


def list_datasets(language: str = "en") -> list[dict[str, Any]]:
    return [spec.to_dict(language) for spec in _DATASETS]


def get_dataset_spec(dataset_id: str) -> DatasetSpec:
    for spec in _DATASETS:
        if spec.dataset_id == dataset_id:
            return spec
    from .errors import AgentForecastError
    raise AgentForecastError(
        code="DATASET_NOT_FOUND",
        message=f"Unknown dataset '{dataset_id}'.",
        help_text="Use 'agentforecast list-datasets' to inspect bundled datasets.",
    )


def dataset_path(dataset_id: str) -> Path:
    spec = get_dataset_spec(dataset_id)
    return Path(resources.files("agentforecast.package_data.datasets").joinpath(spec.file_name))


def write_dataset(dataset_id: str, outdir: str | Path = ".") -> Path:
    src = dataset_path(dataset_id)
    target_dir = Path(outdir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / src.name
    shutil.copyfile(src, target)
    return target
