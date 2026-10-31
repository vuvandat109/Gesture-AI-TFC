
# Gesture AI TF-C — Hand Gesture Recognition

A web-based hand gesture recognition system powered by **TF-C (Time-Frequency Consistency)** and motion sensor data collected using Sensor Logger.

The application recognizes five hand gestures using accelerometer and gyroscope measurements. It provides user authentication, sensor data upload, gesture classification, and prediction confidence scores.

This project is developed from [Gesture-AI-Web](https://github.com/vuvandat109/Gesture-AI-Web). The original user interface, authentication system, database integration, and API structure are preserved, while the previous PCA-based classifier is replaced with a trained neural TF-C model.

**The trained TF-C model is included in this repository. Retraining is not required to run the application.**

## Features

- Recognition of five gestures: **Up, Down, Left, Right, and Rotate**.
- Six-channel motion sensor processing.
- CSV, TXT, and Sensor Logger ZIP file uploads.
- Gesture predictions with class probabilities.
- User registration, login, and logout.
- Password hashing and CSRF protection.
- SQLite and PostgreSQL database support.
- Flask-based prediction API.
- Support for deployment on Render.

## Model Architecture

The system uses **TF-C (Time-Frequency Consistency)**, a self-supervised contrastive learning method designed to learn meaningful representations from time-series data.

TF-C processes sensor signals in both the time and frequency domains before supervised fine-tuning for gesture classification.

### Processing Pipeline

Sensor Data → Preprocessing → Time/Frequency Views → TF-C Pre-training → Fine-tuning → Gesture Classification → Prediction

### Model Configuration

| Component | Configuration |
| --- | --- |
| Input shape | 178 time steps × 6 channels |
| Sensor channels | acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z |
| Gesture classes | 5 |
| Total dataset | 26,000 samples |
| Pre-training dataset | 20,800 unlabeled samples |
| Fine-tuning dataset | 5,200 labeled samples |
| Training split | 3,120 samples |
| Validation split | 1,040 samples |
| Test split | 1,040 samples |
| Pre-training epochs | 40 |
| Fine-tuning epochs | 40 |
| Framework | PyTorch |

### Experimental Results

| Metric | Result |
| --- | ---: |
| Test Accuracy | **39.62%** |
| Test Macro-F1 | **39.75%** |
| Selected Checkpoint | Epoch 34 |
| Test Samples | 1,040 |
| Previous PCA Baseline Accuracy | 49.23% |

The TF-C training pipeline was completed successfully. However, this experiment did not outperform the previous PCA baseline.

The dataset contains augmented and synthetic-derived samples, and original participant/session identifiers are incomplete. Therefore, the reported results should not be interpreted as independent-user evaluation performance.

Detailed training results are available in:

- [Training Report](models/training_report.json)
- [TF-C Training Documentation](docs/TFC_RETRAINING.md)
- [Release Validation Report](docs/RELEASE_VALIDATION.json)

## Installation

### Requirements

- Python 3.12 (64-bit)
- Git
- Python dependencies listed in `requirements.txt`

### Clone the Repository

```bash
git clone https://github.com/vuvandat109/Gesture-AI-TFC.git
cd Gesture-AI-TFC
```

### Windows Installation

Create a virtual environment:

```powershell
py -3.12 -m venv .venv
```

Install dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Verify the trained model:

```powershell
.\.venv\Scripts\python.exe scripts/verify_tfc_release.py
.\.venv\Scripts\python.exe scripts/verify_preserved_assets.py
```

Start the application:

```powershell
.\.venv\Scripts\python.exe app.py
```

### macOS / Linux Installation

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/verify_tfc_release.py
.venv/bin/python app.py
```

Open the application in your browser:

http://127.0.0.1:5000

## How to Use

1. Open the application and register an account.
2. Log in using your registered credentials.
3. Upload a compatible sensor data file.
4. Run the gesture prediction.
5. View the predicted gesture and confidence scores.

### Supported Input Formats

The application supports:

- **CSV/TXT:** Six-channel accelerometer and gyroscope measurements.
- **ZIP:** Sensor Logger exports containing `Accelerometer.csv` and `Gyroscope.csv`.

Input requirements:

- Minimum: 20 rows.
- Maximum: 10,000 rows.
- Maximum upload size: 5 MB.
- Six motion sensor channels are required.

The application preprocesses the input into a 178-step window before inference.

The complete training dataset is not intended to be uploaded through the prediction interface.

## Deployment on Render

The application can be deployed as a Python web service on Render.

### Build Command

```bash
pip install -r requirements.txt && python scripts/verify_tfc_release.py
```

### Start Command

```bash
python -m gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120
```

### Environment Variables

| Variable | Description |
| --- | --- |
| `SECRET_KEY` | Secure application secret key |
| `COOKIE_SECURE` | Set to `1` when using HTTPS |
| `DATABASE_URL` | PostgreSQL database connection URL |

Generate a secure secret key using:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Do not commit secret keys, database credentials, or production configuration files to GitHub.

For persistent account storage and account migration, see [Account Storage Documentation](docs/ACCOUNT_STORAGE.md).

### Deployment Verification

After deployment, access:

```text
/api/health
```

Verify that:

- `model_ready` is `true`.
- The model name contains `TF-C`.
- The prediction API responds correctly.

**Note:** The trained model is available in the repository, but successful deployment on a new Render service has not yet been independently verified.

## Model Training

The TF-C model uses two training stages.

### Stage 1: Self-Supervised Pre-training

The model learns time-domain and frequency-domain representations from unlabeled sensor data through contrastive learning.

- Dataset: 20,800 unlabeled samples.
- Epochs: 40.
- Objective: TF-C contrastive learning.

### Stage 2: Supervised Fine-tuning

The pretrained model is fine-tuned using labeled gesture data and cross-entropy loss.

- Labeled dataset: 5,200 samples.
- Training samples: 3,120.
- Validation samples: 1,040.
- Test samples: 1,040.
- Epochs: 40.

### Retraining Command

Place the original dataset at:

```text
datasets/Sensor_logger.zip
```

Then run:

```bash
python train_tfc.py --data datasets/Sensor_logger.zip --pre-epochs 40 --fine-epochs 40 --threads 4
```

Verify the generated model:

```bash
python scripts/verify_tfc_release.py
```

The original training archive is not included in standard Git commits because of its size. The repository contains the trained model and checkpoints.

## Model Files

| File | Description |
| --- | --- |
| `models/gesture_real_v1.joblib` | Trained TF-C inference model |
| `models/tfc_pretrained.pt` | Pre-training checkpoint |
| `models/tfc_finetuned.pt` | Fine-tuning checkpoint |
| `models/training_history.json` | Training logs |
| `models/training_report.json` | Training and evaluation metrics |
| `models/classification_report.json` | Classification report |
| `models/evaluation_split.csv` | Dataset split information |

The previous PCA model is preserved in `models/baseline_pca/` for comparison.

## Testing

Run the following commands to verify the system:

```bash
python -m unittest test_sensor_model.py
python tests/test_application.py
python tests/test_tfc.py
python tests/test_tfc_release.py
node tests/test_auth_ui.js
python scripts/verify_tfc_release.py
python scripts/verify_preserved_assets.py
```

The tests cover:

- Sensor data preprocessing.
- TF-C model integrity.
- Model serialization and inference.
- API functionality.
- User authentication.
- Preserved interface assets.
- Checkpoint consistency.

Recorded validation results can be found in [Release Validation](docs/RELEASE_VALIDATION.json).

## Project Structure

```text
Gesture-AI-TFC/
├── app.py
├── tfc_model.py
├── train_tfc.py
├── sensor_input.py
├── models/
│   ├── gesture_real_v1.joblib
│   ├── tfc_pretrained.pt
│   ├── tfc_finetuned.pt
│   ├── training_history.json
│   ├── training_report.json
│   └── baseline_pca/
├── templates/
├── static/
├── scripts/
├── tests/
├── docs/
└── requirements.txt
```

## Technologies Used

| Technology | Purpose |
| --- | --- |
| Python | Main programming language |
| PyTorch | Deep learning and TF-C |
| NumPy | Numerical computation |
| Pandas | Data processing |
| Flask | Backend and REST API |
| HTML, CSS, JavaScript | Frontend |
| SQLite / PostgreSQL | User account storage |
| GitHub | Source code management |
| Render | Web deployment |

## References

1. Zhang, X., Zhao, Z., Tsiligkaridis, T., & Zitnik, M. (2022). *Self-Supervised Contrastive Pre-Training For Time Series via Time-Frequency Consistency*. [arXiv:2206.08496](https://arxiv.org/abs/2206.08496).
2. [TF-C Official Implementation](https://github.com/mims-harvard/TFC-pretraining).
3. [Gesture-AI-Web Original Repository](https://github.com/vuvandat109/Gesture-AI-Web).

---

**Project:** Gesture AI TF-C — Hand Gesture Recognition

**Repository:** https://github.com/vuvandat109/Gesture-AI-TFC
