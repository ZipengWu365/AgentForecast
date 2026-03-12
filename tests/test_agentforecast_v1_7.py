from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from agentforecast import ConformalSpec, FeatureSpec, forecast_dataset, shoot
from agentforecast.backends import is_backend_available, list_backends, route_backends
from agentforecast.datasets import dataset_path, get_dataset_spec
from agentforecast.features import build_feature_spec, prepare_series_frame
from agentforecast.hosted import build_hosted_site
from agentforecast.local import compare_backends_dataset, forecast_stream_csv
from agentforecast.mcp_server import dispatch_jsonrpc
from agentforecast.tool_server import dispatch_tool_call

TSFRESH_AVAILABLE = importlib.util.find_spec("tsfresh") is not None


class AgentForecastV17Tests(unittest.TestCase):
    def test_forecast_dataset(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = forecast_dataset('sales', outdir=tmp)
            self.assertIn('headline', result.summary)
            self.assertEqual(result.inputs['dataset_id'], 'sales')
            self.assertTrue((Path(tmp) / 'sales' / 'meta' / 'metadata.json').exists())

    def test_compare_backends_dataset(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = compare_backends_dataset('gold', backends=['naive', 'moving_average', 'stats_arima'], outdir=tmp)
            self.assertGreaterEqual(len(result.leaderboard), 2)
            self.assertIn(result.backend_selected, [row['backend_id'] for row in result.leaderboard])

    def test_route_backends(self) -> None:
        route = route_backends(history_len=50, horizon=14, strategy='streaming', exogenous_cols=[])
        self.assertIn('candidate_backends', route)
        self.assertIn('stream_ewm', route['candidate_backends'])

    def test_list_backends_contains_new_entries(self) -> None:
        backend_ids = {row['backend_id'] for row in list_backends()}
        self.assertIn('stream_ewm', backend_ids)
        self.assertIn('statsforecast_autoarima', backend_ids)
        self.assertIn('mlforecast_linear', backend_ids)

    def test_forecast_stream_builtin(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = forecast_stream_csv(dataset_path('icu-bed-stress'), backend='stream_ewm', outdir=tmp)
            self.assertEqual(result.backend_selected, 'stream_ewm')
            self.assertIn('streaming', result.diagnostics)

    def test_tool_server_error_shape(self) -> None:
        payload = dispatch_tool_call('nope', {})
        self.assertFalse(payload['ok'])
        self.assertEqual(payload['error']['code'], 'TOOL_NOT_FOUND')
        self.assertIn('schema_ref', payload['error'])
        self.assertIn('retryable', payload['error'])

    def test_mcp_resources(self) -> None:
        response = dispatch_jsonrpc({'jsonrpc': '2.0', 'id': 1, 'method': 'resources/list'})
        self.assertIn('result', response)
        resources = response['result']['resources']
        self.assertTrue(any(item['uri'] == 'package://agentforecast/overview' for item in resources))

    def test_build_hosted_site(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runs = Path(tmp) / 'runs'
            site = Path(tmp) / 'site'
            shoot('sales', outdir=runs)
            manifest = build_hosted_site(runs, site)
            self.assertEqual(manifest['entry_count'], 1)
            self.assertTrue((site / 'index.html').exists())
            feed = json.loads((site / 'feed.json').read_text(encoding='utf-8'))
            self.assertEqual(len(feed['items']), 1)

    def test_summary_markdown_is_generated_without_tabulate_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = forecast_dataset('sales', outdir=tmp)
            summary_path = Path(tmp) / 'sales' / 'reports' / 'summary.md'
            text = summary_path.read_text(encoding='utf-8')
            self.assertIn('| backend_id |', text)
            self.assertEqual(result.backend_selected in text, True)

    def test_river_linear_conformal_emits_interval_metrics(self) -> None:
        if not is_backend_available('river_linear'):
            self.skipTest('river extra is not installed')
        with tempfile.TemporaryDirectory() as tmp:
            result = forecast_dataset(
                'sales',
                backend='river_linear',
                outdir=tmp,
                conformal=ConformalSpec(enabled=True, levels=(80, 90, 95), calibration_window=50, warmup_min=5),
            )
            conformal = result.diagnostics['conformal']
            self.assertEqual(conformal['method'], 'river_jackknife')
            self.assertIn('90', conformal['coverage_backtest'])
            self.assertIn('90', conformal['mean_interval_width'])
            forecast_path = Path(tmp) / 'sales' / 'data' / 'forecast.csv'
            forecast_text = forecast_path.read_text(encoding='utf-8')
            self.assertIn('lower_95', forecast_text)
            self.assertIn('upper_95', forecast_text)
            self.assertIn('coverage_90', result.metrics)
            self.assertIn('avg_width_90', result.metrics)

    def test_build_feature_spec_supports_custom_lag_and_delay_features(self) -> None:
        frame = pd.read_csv(dataset_path('gold-exogenous'))
        prepared = prepare_series_frame(frame)
        spec = build_feature_spec(
            prepared.history,
            feature_spec=FeatureSpec(
                lag_points=(1, 5, 9),
                lag_step=7,
                lag_count=4,
                rolling_windows=(3, 8, 21),
                include_tsfresh=TSFRESH_AVAILABLE,
                tsfresh_window=21,
            ),
        )
        self.assertEqual(spec['lags'], [1, 5, 7, 9, 14, 21, 28])
        self.assertEqual(spec['rolling_windows'], [3, 8, 21])
        self.assertEqual(spec['lag_step'], 7)
        self.assertEqual(spec['lag_count'], 4)
        self.assertEqual(spec['include_tsfresh'], TSFRESH_AVAILABLE)
        if TSFRESH_AVAILABLE:
            self.assertIn('sample_entropy', spec['tsfresh_features'])

    def test_forecast_dataset_accepts_custom_feature_spec(self) -> None:
        custom = FeatureSpec(
            lag_points=(1, 2, 7, 14),
            lag_step=14,
            lag_count=3,
            rolling_windows=(3, 7, 14),
            include_tsfresh=TSFRESH_AVAILABLE,
            tsfresh_window=21,
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = forecast_dataset('gold-exogenous', backend='ml_ridge', outdir=tmp, feature_spec=custom)
            self.assertEqual(result.feature_spec['lag_step'], 14)
            self.assertEqual(result.feature_spec['lag_count'], 3)
            self.assertIn(14, result.feature_spec['lags'])
            self.assertEqual(result.feature_spec['include_tsfresh'], TSFRESH_AVAILABLE)

    def test_time_series_regression_case_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = shoot('time-series-regression-lab', outdir=tmp)
            self.assertEqual(result.feature_spec['mode'], 'time_series_regression_lab')
            self.assertIn(result.backend_selected, result.candidate_backends)
            self.assertIn('lags', result.feature_spec)

    def test_new_cross_domain_dataset_specs_exist(self) -> None:
        for dataset_id in ['gold-exogenous', 'grid-heatwave-stress', 'river-flood-risk', 'outpatient-no-show']:
            spec = get_dataset_spec(dataset_id)
            self.assertTrue(spec.provenance_en)


if __name__ == '__main__':
    unittest.main()
