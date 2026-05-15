from kafka import KafkaProducer
import pandas as pd
import json, time

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

df = pd.read_csv('data/city_day.csv')
df['Date'] = pd.to_datetime(df['Date'])
df_city = df[df['City'] == 'Delhi'][['Date', 'PM2.5']].dropna()
df_city = df_city.sort_values('Date')

print(f"Bắt đầu gửi {len(df_city)} bản ghi lên Kafka...")

for _, row in df_city.iterrows():
    record = {
        'date': str(row['Date'].date()),
        'pm25': round(row['PM2.5'], 2)
    }
    producer.send('pm25-topic', value=record)
    print(f"Đã gửi: {record}")
    time.sleep(0.1)

producer.flush()
print("Gửi xong!")
