from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, count, col, to_date, date_format, from_json
from pyspark.sql.types import *
import os
import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import mean_squared_error, mean_absolute_error

spark = SparkSession.builder \
    .appName('PM25Streaming') \
    .config('spark.jars.packages',
            'org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0') \
    .getOrCreate()

spark.sparkContext.setLogLevel('ERROR')
print('Spark started!')

schema = StructType([
    StructField('date', StringType()),
    StructField('pm25', DoubleType())
])

df_raw = spark.readStream \
    .format('kafka') \
    .option('kafka.bootstrap.servers', 'localhost:9092') \
    .option('subscribe', 'pm25-topic') \
    .option('startingOffsets', 'earliest') \
    .load()

df_parsed = df_raw.select(
    from_json(col('value').cast('string'), schema).alias('data')
).select('data.*')

df_with_month = df_parsed \
    .withColumn('date', to_date('date')) \
    .withColumn('month', date_format('date', 'yyyy-MM'))

df_monthly = df_with_month \
    .groupBy('month') \
    .agg(
        avg('pm25').alias('avg_pm25'),
        count('pm25').alias('day_count')
    )

def process_batch(batch_df, batch_id):
    if batch_df.count() == 0:
        return
    pdf = batch_df.toPandas().sort_values('month').reset_index(drop=True)
    completed = pdf[pdf['day_count'] >= 28].reset_index(drop=True)
    if len(completed) < 24:
        print(f"Batch {batch_id}: chua du data ({len(completed)} thang), can it nhat 24")
        return
    rows = []
    for i in range(24, len(completed)):
        train_data = completed['avg_pm25'][:i].values
        try:
            model = ExponentialSmoothing(
                train_data,
                trend='mul',
                seasonal='mul',
                seasonal_periods=12
            ).fit(optimized=True)
            forecast_val = float(model.forecast(1)[0])
            actual_val = float(completed.loc[i, 'avg_pm25'])
            rows.append({
                'month': completed.loc[i, 'month'],
                'avg_pm25_actual': round(actual_val, 2),
                'forecast_next_month': round(forecast_val, 2)
            })
            print(f"Thang {completed.loc[i, 'month']}: Actual={actual_val:.2f}, Forecast={forecast_val:.2f}")
        except Exception as e:
            print(f"Loi thang {completed.loc[i, 'month']}: {e}")
            continue
    if len(rows) == 0:
        return
    out_df = pd.DataFrame(rows)
    rmse = np.sqrt(mean_squared_error(out_df['avg_pm25_actual'], out_df['forecast_next_month']))
    mae = mean_absolute_error(out_df['avg_pm25_actual'], out_df['forecast_next_month'])
    mape = np.mean(np.abs((out_df['avg_pm25_actual'] - out_df['forecast_next_month']) / out_df['avg_pm25_actual'])) * 100
    print(f"\n=== Batch {batch_id} Metrics ===")
    print(f"RMSE: {rmse:.2f}")
    print(f"MAE:  {mae:.2f}")
    print(f"MAPE: {mape:.2f}%")
    os.makedirs('output', exist_ok=True)
    out_df.to_csv('output/results.csv', index=False)
    print(f"Da luu {len(rows)} dong vao output/results.csv")

query = df_monthly.writeStream \
    .foreachBatch(process_batch) \
    .outputMode('complete') \
    .trigger(processingTime='10 seconds') \
    .start()

print("Spark Streaming dang chay... Cho data tu Kafka")
query.awaitTermination()
