import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import mean_squared_error, mean_absolute_error
import joblib, os

# Đọc dữ liệu
df = pd.read_csv('data/city_day.csv')
df['Date'] = pd.to_datetime(df['Date'])

# Chọn Delhi vì có đủ dữ liệu nhiều năm
CITY = 'Delhi'
print(f"Thành phố được chọn: {CITY}")

# Lọc và xử lý missing
df_city = df[df['City'] == CITY][['Date', 'PM2.5']].copy()
df_city = df_city.sort_values('Date')
df_city['PM2.5'] = df_city['PM2.5'].interpolate(method='linear')

# Aggregate theo tháng
df_city['Month'] = df_city['Date'].dt.to_period('M')
monthly = df_city.groupby('Month')['PM2.5'].mean()
monthly.index = monthly.index.to_timestamp()

print(f"Số tháng dữ liệu: {len(monthly)}")
print(monthly)

# Chia train/test
split = int(len(monthly) * 0.8)
train = monthly[:split]
test  = monthly[split:]

# Train Holt-Winters
model = ExponentialSmoothing(
    train,
    trend='mul',
    seasonal='mul',
    seasonal_periods=12
).fit(optimized=True)

# Đánh giá
pred = model.forecast(len(test))
rmse = np.sqrt(mean_squared_error(test, pred))
mae  = mean_absolute_error(test, pred)
print(f"\n=== Kết quả đánh giá ===")
print(f"RMSE: {rmse:.4f}")
print(f"MAE:  {mae:.4f}")

# Lưu model
os.makedirs('model', exist_ok=True)
joblib.dump(model, 'model/holtwinters.pkl')
joblib.dump(CITY, 'model/city.pkl')
print(f"\nModel đã lưu: model/holtwinters.pkl")
