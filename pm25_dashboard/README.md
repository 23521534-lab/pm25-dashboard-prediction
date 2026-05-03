# 🌫️ PM2.5 Forecast Dashboard — IE212 Nhóm 6

Dashboard Streamlit để demo kết quả đồ án Big Data: dự báo PM2.5 bằng Statistical và Deep Learning models.

---

## 📦 Cài đặt & Chạy (3 bước)

### Bước 1 — Cài thư viện
Mở terminal, cd vào thư mục này rồi chạy:
```bash
pip install -r requirements.txt
```

### Bước 2 — Chuẩn bị dữ liệu (tuỳ chọn)
Nếu nhóm có file `results.csv` từ Spark pipeline, copy vào thư mục `output/`:
```
pm25_dashboard/
├── output/
│   └── results.csv     ← file này
└── app.py
```

Nếu không có file này, dashboard sẽ tự tạo dữ liệu demo.

### Bước 3 — Chạy dashboard
```bash
streamlit run app.py
```

Trình duyệt sẽ tự mở tại: **http://localhost:8501**

---

## 📊 Tính năng Dashboard

| Tab | Nội dung |
|-----|----------|
| 📊 Kết quả Pipeline | Biểu đồ Actual vs Predicted, RMSE/MAE/MAPE, residuals |
| 🔮 Dự báo Real-time | Nhập PM10/NOx/NO2/NH3 → dự báo PM2.5 ngay lập tức |
| 📈 So sánh Mô hình | Bảng + biểu đồ so sánh 8 mô hình (AR, SARIMA, LSTM...) |
| 📋 Thông tin Dataset | Dataset info, train/test split, pipeline architecture |

---

## 🎥 Ghi video demo

1. Chạy `streamlit run app.py`
2. Mở OBS / Loom / built-in screen recorder
3. Demo theo thứ tự:
   - Tab 1: Giải thích pipeline, chỉ ra RMSE/MAE
   - Tab 3: So sánh 8 mô hình → nói lý do chọn Stacked LSTM
   - Tab 2: Nhập số liệu thực → xem dự báo PM2.5
   - Tab 4: Giải thích dataset và pipeline architecture

---

## 📁 Cấu trúc thư mục

```
pm25_dashboard/
├── app.py                  # Main dashboard
├── requirements.txt        # Dependencies
├── README.md               # File này
├── output/
│   └── results.csv         # Kết quả từ Spark (copy vào đây)
└── sample_data/
    └── results.csv         # Dữ liệu demo (dùng khi chưa có output)
```
