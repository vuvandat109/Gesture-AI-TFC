"""Use unfiltered held-out samples to compare stored predictions with the web API."""
import argparse
import io
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tests'))
from test_application import FunctionalTests
from tfc_model import CLASSES


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=Path, default=ROOT / 'datasets/Sensor_logger.zip')
    args = parser.parse_args()
    saved = np.load(ROOT / 'models/test_predictions.npz')
    case = FunctionalTests()
    case.setUp()
    assert case.login().status_code == 200
    checks = []
    with zipfile.ZipFile(args.data) as archive:
        roots = [name[:-len('fine_tuning/index.csv')] for name in archive.namelist() if name.endswith('fine_tuning/index.csv')]
        assert len(roots) == 1
        prefix = roots[0]
        index = pd.read_csv(io.BytesIO(archive.read(prefix + 'fine_tuning/index.csv')))
        for label in range(5):
            pos = int(np.flatnonzero(saved['labels'] == label)[0])
            row = index.iloc[int(saved['indices'][pos])]
            data = archive.read(prefix + 'fine_tuning/' + row.file)
            response = case.upload(data, 'heldout.csv')
            assert response.status_code == 200, response.get_json()
            result = response.get_json()
            expected = saved['probabilities'][pos]
            assert result['gesture_key'] == CLASSES[int(expected.argmax())]
            for item in result['probabilities']:
                value = round(float(expected[CLASSES.index(item['key'])]) * 100, 2)
                assert abs(item['probability'] - value) <= .011
            checks.append({'sample_id': str(row.sample_id), 'true_key': CLASSES[label],
                           'predicted_key': result['gesture_key'], 'http_status': 200,
                           'matches_saved_inference': True})
    print(json.dumps({'checks': checks, 'note': 'First held-out sample per true class, without selecting correct predictions. This is an integration check, not an accuracy estimate.'}, indent=2))


if __name__ == '__main__':
    main()
