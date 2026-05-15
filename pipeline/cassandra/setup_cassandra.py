from cassandra.cluster import Cluster
import time

print("Connecting to Cassandra...")
cluster = Cluster(['localhost'])
session = cluster.connect()

session.execute("""
    CREATE KEYSPACE IF NOT EXISTS pm25
    WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}
""")

session.set_keyspace('pm25')

session.execute("""
    CREATE TABLE IF NOT EXISTS forecast_results (
        month TEXT PRIMARY KEY,
        avg_pm25_actual DOUBLE,
        forecast_next_month DOUBLE
    )
""")

print("Keyspace 'pm25' và table 'forecast_results' đã tạo xong!")
cluster.shutdown()
