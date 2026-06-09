# PM2.5 Forecast Dashboard
IE212 - Công nghệ Dữ liệu Lớn · Nhóm 6

[![Streamlit App](https://img.shields.io/badge/Streamlit-Demo-red?logo=streamlit)](https://pm25-forecast-dashboard.streamlit.app/)

Dashboard trực quan hóa kết quả dự báo PM2.5 sử dụng các mô hình thống kê và học sâu, tích hợp với pipeline Big Data (Kafka → Spark → Model).

## Tính năng

- **Kết quả Pipeline**: Biểu đồ Actual vs Predicted từ Spark output, các chỉ số RMSE/MAE/MAPE
- **Dự báo Real-time**: Nhập PM10, NOx, NO2, NH3 → dự báo PM2.5 bằng AR(3) và Stacked LSTM
- **So sánh Mô hình**: So sánh 10 mô hình (AR, SARIMA, Holt-Winters, Prophet, Vanilla LSTM, Stacked LSTM, Bi-LSTM, CNN-LSTM, GRU, Hybrid)
- **Thông tin Dataset**: Mô tả dataset, phân chia train/test, kiến trúc pipeline

## Dataset

Air Quality India · Kaggle · 29,531 mẫu · 2015–2020 · 26 thành phố
