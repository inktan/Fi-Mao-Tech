import psycopg2
import os

# 数据库连接参数
hostname = '10.1.12.30'
database = 'your_database'
username = 'postgres'
password = "ppp"
port_id = 5432

# 连接到数据库
conn = psycopg2.connect(
    host=hostname,
    dbname=database,
    user=username,
    # password="password",
    port=port_id
    
)