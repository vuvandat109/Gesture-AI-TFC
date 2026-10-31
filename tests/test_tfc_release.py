"""Check the trained network, exported adapter, and authenticated API agree."""
import io
import json
import sys
import unittest
from pathlib import Path

import joblib
import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).parent))
from tfc_model import CLASSES, GestureTFC, TFCInference, prepare_window
import test_application as application_tests

csv_data = application_tests.csv_data
web = application_tests.web


class TrainedReleaseTests(unittest.TestCase):
    def test_network_export_and_api_agree(self):
        bundle = joblib.load(ROOT / 'models/gesture_real_v1.joblib')
        self.assertIsInstance(bundle['model'], TFCInference)
        self.assertEqual(bundle['info']['feature_version'], 'tfc6_v1')
        raw = np.loadtxt(io.BytesIO(csv_data()), delimiter=',', skiprows=1)
        window = prepare_window(raw).reshape(1, -1)
        adapter_probs = bundle['model'].predict_proba(window)[0]
        checkpoint = torch.load(ROOT / 'models/tfc_finetuned.pt', weights_only=True, map_location='cpu')
        net = GestureTFC().eval()
        net.load_state_dict(checkpoint['model_state_dict'])
        with torch.inference_mode():
            direct = net(torch.from_numpy(window.reshape(1, 6, 178))).softmax(1).numpy()[0]
        np.testing.assert_allclose(adapter_probs, direct, atol=1e-7)
        case = application_tests.FunctionalTests()
        case.setUp()
        self.assertEqual(case.login().status_code, 200)
        response = case.upload()
        self.assertEqual(response.status_code, 200)
        result = response.get_json()
        self.assertEqual(result['gesture_key'], CLASSES[int(direct.argmax())])
        for item in result['probabilities']:
            self.assertAlmostEqual(item['probability'], round(float(direct[CLASSES.index(item['key'])]) * 100, 2))
        self.assertTrue(result['gyro_used_by_model'])
        self.assertIn('TF-C', result['model_name'])

    def test_report_matches_saved_test_predictions(self):
        report = json.loads((ROOT / 'models/training_report.json').read_text())
        saved = np.load(ROOT / 'models/test_predictions.npz')
        probs, labels = saved['probabilities'], saved['labels']
        self.assertEqual(probs.shape, (1040, 5))
        np.testing.assert_allclose(probs.sum(1), 1, atol=1e-6)
        self.assertAlmostEqual(float((probs.argmax(1) == labels).mean()), report['heldout_test_accuracy'])

    def test_baseline_cannot_be_serving_adapter(self):
        self.assertIsInstance(web.MODEL, TFCInference)
        self.assertEqual(web.INFO['feature_version'], 'tfc6_v1')


if __name__ == '__main__':
    unittest.main()
