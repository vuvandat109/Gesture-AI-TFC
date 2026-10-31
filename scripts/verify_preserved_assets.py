"""Check original source assets and optional dataset against the saved hashes."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    manifest = json.loads((ROOT / 'docs/source_manifest.json').read_text())
    for name, expected in manifest['preserved_files'].items():
        assert digest(ROOT / name) == expected, f'Changed original asset: {name}'
    for original, retained in manifest['retained_originals'].items():
        assert digest(ROOT / retained['path']) == retained['sha256'], original
    dataset = ROOT / 'datasets/Sensor_logger.zip'
    if dataset.exists():
        assert digest(dataset) == manifest['dataset_sha256'], 'Dataset bytes changed'
        print('PASS: original Sensor Logger ZIP SHA-256 matches')
    else:
        print('Dataset not present locally; source/model checks still run. See README.')
    print(f"PASS: {len(manifest['preserved_files'])} original files unchanged, including all UI assets")


if __name__ == '__main__':
    main()
