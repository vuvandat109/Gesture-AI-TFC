# TF-C trên Sensor Logger 6 kênh

Huấn luyện lại từ đầu ngày 31/10/2026 bằng bản ZIP gốc của người dùng. Kết quả của lần chạy này nằm trong `models/training_report.json`; không sử dụng số liệu của lần chạy trước.

## Dữ liệu và phép chia

- Bản gốc: `datasets/Sensor_logger.zip`, giữ nguyên byte. SHA-256: `451c770fedf11b305a8d03ab5cb79140671d23686bcce6242443f0540918e643`.
- 20.800 cửa sổ không nhãn để pre-training; 5.200 cửa sổ có nhãn, mỗi nhãn 1.040 mẫu.
- Fine-tuning: 3.120 train / 1.040 validation / 1.040 test. Tách theo tổ tiên augmentation có trong manifest, seed 42/43. Chọn checkpoint bằng macro-F1 validation; chỉ đánh giá test ở cuối.
- Mỗi mẫu: 178 bước × 6 kênh `acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z`. Không đổi nhãn nguồn; chỉ ánh xạ tên `rotate` thành khóa API `circle` để tương thích giao diện cũ.
- Kiểm tra 24 mẫu CSV so với NPY, tính hash ZIP, kiểm tra trùng mẫu chính xác và tổ tiên đã biết giữa pre-training và held-out.
- Dữ liệu có augmentation; thiếu ID bản ghi/session gốc. Không thể loại trừ quan hệ nguồn chưa được ghi trong manifest. Đây không phải đánh giá trên người dùng/session hoàn toàn độc lập.

## Mạng và huấn luyện

Hai Transformer encoder học biểu diễn thời gian và biên độ FFT, mỗi encoder có hai lớp; hai projector 128 chiều; ghép hai biểu diễn qua MLP phân loại 5 lớp. `batch_first=True` để các mẫu không tương tác với nhau qua trục batch.

Pre-training dùng NT-Xent thời gian, NT-Xent tần số và time-frequency consistency theo phương trình 1–4 của bài báo TF-C. Fine-tuning cập nhật cả hai encoder, projector và bộ phân loại bằng cross-entropy. Đây là bản điều chỉnh 6 kênh cho Sensor Logger, không phải bản tái lập điểm benchmark trong bài báo.

- 40 epoch pre-training + 40 epoch fine-tuning.
- Batch 128, Adam lr 0,0003, betas (0,9; 0,99), seed 42.
- Lambda 0,2; temperature 0,2; margin 1,0.
- Z-score từng cửa sổ, cùng một hàm `prepare_window` khi train và khi dự đoán.
- Augmentation thời gian: jitter, scale, circular shift, permutation 4 đoạn. Augmentation tần số: thêm hoặc bỏ 10% bin.

## Tệp kết quả

| Tệp | Vai trò |
|---|---|
| `tfc_pretrained.pt` | Trọng số encoder sau pre-training |
| `tfc_finetuned.pt` | Toàn mạng tại epoch được chọn trên validation |
| `gesture_real_v1.joblib` | Adapter TF-C dùng trực tiếp bởi web |
| `training_history.json` | Loss và chỉ số từng epoch |
| `training_report.json` | Cấu hình, kết quả, hash trọng số, bằng chứng trọng số đã cập nhật |
| `data_audit.json` | Kiểm tra dữ liệu đầu vào và giới hạn đánh giá |
| `classification_report.json` | Precision/recall/F1 từng lớp |
| `evaluation_split.csv` | Sample ID, augmentation ancestor và phép chia |
| `test_predictions.npz` | Xác suất và nhãn test để kiểm tra lại báo cáo |

Để huấn luyện lại: `python train_tfc.py --data datasets/Sensor_logger.zip --pre-epochs 40 --fine-epochs 40 --threads 4`.

Để xác minh bản đã huấn luyện: `python scripts/verify_tfc_release.py`.

## Nguồn phương pháp

- Zhang et al., *Self-Supervised Contrastive Pre-Training for Time Series via Time-Frequency Consistency*, NeurIPS 2022: https://arxiv.org/abs/2206.08496
- Mã nguồn tham khảo: https://github.com/mims-harvard/TFC-pretraining ; giấy phép upstream lưu tại `third_party/TFC_LICENSE`.

Mã PCA và tài liệu cũ được giữ để tham khảo; bản baseline cũ nằm trong `models/baseline_pca`. API chỉ chấp nhận adapter TF-C, không tự chuyển về PCA.
