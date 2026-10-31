# Gesture AI TF-C — bản riêng để đưa lên GitHub mới

Bản sao từ `vuvandat109/Gesture-AI-Web`, nhánh `main`, commit `50b2db70d5d571b8f90338e83f174599826d630f`. Giữ nguyên giao diện, CSS/JS, hình minh họa, đăng ký/đăng nhập, CSRF, SQLite/PostgreSQL và định dạng API. Thay mô hình đang phục vụ bằng **TF-C Time-Frequency Consistency, 6 kênh**.

**Đã kèm model huấn luyện. Không cần train lại để chạy web.** Lần chạy này hoàn thành 40 epoch pre-training + 40 epoch fine-tuning: accuracy test **39.62%**, macro-F1 **39.75%**, checkpoint epoch 34. PCA cũ đạt 49,23% trên bộ dữ liệu hiện có; TF-C lần này chưa vượt baseline. Kết quả của lần huấn luyện mới nằm tại [models/training_report.json](models/training_report.json). Chi tiết phương pháp: [docs/TFC_RETRAINING.md](docs/TFC_RETRAINING.md).

## 1. Chạy trên Windows

Cài Python **3.12 (64-bit)** và Git. Giải nén bản đầy đủ, mở PowerShell tại thư mục có `app.py`:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/verify_tfc_release.py
.\.venv\Scripts\python.exe scripts/verify_preserved_assets.py
.\.venv\Scripts\python.exe app.py
```

Mở http://127.0.0.1:5000. Đăng ký tài khoản, đăng nhập và tải một cử chỉ bằng CSV/TXT 6 kênh hoặc ZIP Sensor Logger có `Accelerometer.csv` + `Gyroscope.csv`. Tệp phải có 20–10.000 dòng; giới hạn tải lên 5 MB. Bộ dữ liệu huấn luyện 449 MB không phải tệp đầu vào để tải vào ô dự đoán.

Chạy trên macOS/Linux: dùng `python3 -m venv .venv`, `.venv/bin/python -m pip install -r requirements.txt`, rồi `.venv/bin/python app.py`.

## 2. Đưa toàn bộ mã và model lên repo MỚI

Trên GitHub, tạo repo trống, ví dụ **Gesture-AI-TFC**. Không chọn tạo sẵn README/license/gitignore. Thư mục giải nén không chứa `.git` hay remote của repo cũ.

```powershell
git init -b main
git add .
git commit -m "Create Gesture AI TF-C with trained model"
git remote add origin https://github.com/vuvandat109/Gesture-AI-TFC.git
git push -u origin main
```

Thay URL bằng repo mới thực tế. Nếu Git hỏi danh tính, đặt `git config user.name "TEN_CUA_BAN"` và `git config user.email "EMAIL_GITHUB_CUA_BAN"`, rồi chạy lại commit/push. Đăng nhập GitHub khi Git yêu cầu.

Hoặc, sau khi kích hoạt môi trường Python, dùng script kiểm tra model và đẩy lên repo trống:

```powershell
.\.venv\Scripts\Activate.ps1
.\push_new_repo.ps1 -RepositoryUrl https://github.com/vuvandat109/Gesture-AI-TFC.git
```

Chỉ chạy script này trên thư mục vừa giải nén, chưa `git init`. Nếu PowerShell không cho chạy script, dùng các lệnh Git thủ công phía trên.

**Dữ liệu gốc:** bản đầy đủ chứa `datasets/Sensor_logger.zip`, giữ nguyên byte và được kiểm tra SHA-256. Thư mục `datasets/` được bỏ qua khi push vì ZIP gốc lớn hơn giới hạn 100 MB mỗi tệp của GitHub. Mã nguồn, trọng số và mọi báo cáo huấn luyện vẫn được đẩy bình thường. Giữ ZIP ở máy để train lại; nếu cần lưu ZIP cùng repo, cấu hình Git LFS cho `datasets/*.zip` và kiểm tra dung lượng tài khoản trước khi bỏ quy tắc ignore. Bản mã + model gọn không chứa ZIP này; chép lại bản `Sensor logger.zip` đã gửi, đổi tên thành `datasets/Sensor_logger.zip` để huấn luyện lại.

## 3. Triển khai trên Render

Tạo Web Service mới từ repo mới. Dùng Python 3.12; Build Command:

```bash
pip install -r requirements.txt && python scripts/verify_tfc_release.py
```

Start Command:

```bash
python -m gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120
```

Đặt biến môi trường:

| Biến | Giá trị |
|---|---|
| `SECRET_KEY` | Chuỗi ngẫu nhiên dài, ổn định giữa các lần deploy |
| `COOKIE_SECURE` | `1` khi dùng HTTPS |
| `DATABASE_URL` | PostgreSQL URL nếu muốn lưu tài khoản lâu dài |

Tạo `SECRET_KEY` bằng `python -c "import secrets; print(secrets.token_hex(32))"`. Không đưa khóa hay URL database thật vào Git. Đọc [docs/ACCOUNT_STORAGE.md](docs/ACCOUNT_STORAGE.md) để chuyển dữ liệu tài khoản hiện có. Repo cũ không chứa database tài khoản trên dịch vụ đang chạy; không thể sao chép các tài khoản đó chỉ bằng clone GitHub.

Kiểm tra `/api/health`: `model_ready` phải là `true`, `model` phải chứa `TF-C`. Không cần dữ liệu train trên máy chủ web. PyTorch cần tài nguyên khác mô hình PCA; chọn cấu hình dịch vụ theo mức RAM thực tế trong log. Chưa có kết quả xác minh trên dịch vụ Render mới trong bản bàn giao này.

## 4. Model và train lại

- Mô hình phục vụ: `models/gesture_real_v1.joblib`, chứa **TFCInference**, không còn là PCA/Logistic Regression.
- Trọng số: `models/tfc_pretrained.pt` và `models/tfc_finetuned.pt`.
- Báo cáo, phép chia và dự đoán test: `models/*.json`, `models/evaluation_split.csv`, `models/test_predictions.npz`.
- Bản PCA gốc giữ nguyên trong `models/baseline_pca/` để đối chiếu. Web không tự chuyển về mô hình này.
- Các script huấn luyện PCA/UWave cũ vẫn giữ để tham khảo. Chúng có thể ghi đè model mặc định; không dùng nếu muốn tiếp tục phục vụ TF-C.

```powershell
python train_tfc.py --data datasets/Sensor_logger.zip --pre-epochs 40 --fine-epochs 40 --threads 4
python scripts/verify_tfc_release.py
```

TF-C được điều chỉnh cho 6 kênh Sensor Logger. Không bảo đảm mô hình mới sẽ chính xác hơn PCA; so sánh chỉ số thực tế ở `models/training_report.json` với `models/baseline_pca/training_report.json`. Dữ liệu có augmentation và thiếu ID session gốc nên kết quả không phải đánh giá độc lập trên người dùng mới.

## 5. Kiểm thử

```powershell
python -m unittest test_sensor_model.py
python tests/test_application.py
python tests/test_tfc.py
python tests/test_tfc_release.py
node tests/test_auth_ui.js
python scripts/verify_tfc_release.py
python scripts/verify_preserved_assets.py
```

CI giữ kiểm thử PostgreSQL từ repo cũ và thêm kiểm tra trọng số TF-C. Báo cáo lần kiểm tra bàn giao: `docs/RELEASE_VALIDATION.json`. Các tài liệu trong `docs/testing/` là lịch sử từ repo cũ, không phải số liệu của lần huấn luyện TF-C này. Tài liệu README cũ giữ tại `docs/README_PCA_ORIGINAL.md`.
