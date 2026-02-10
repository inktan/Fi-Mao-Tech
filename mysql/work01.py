import os
import logging
import pandas as pd
import pymysql
from pymysql.err import OperationalError, ProgrammingError
from typing import Tuple, Dict, List
import json

# -------------------------- 1. 基础配置（需手动修改！）--------------------------
# 根路径：你的目标文件夹绝对路径
ROOT_DIR = r"F:\osm\2025年8月份道路矢量数据\分城市的道路数据_50m_svinfo_csv"
MAP_JSON_PATH = r"D:\Users\mslne\Documents\GitHub\Fi-Mao-Tech\mysql\PROVINCE_CITY_MAP.json"  # 省份城市映射JSON文件路径

# MySQL数据库连接信息（替换为你的实际配置）
MYSQL_CONFIG = {
    "host": "localhost",    # 数据库地址，本地填localhost
    "user": "root",         # 数据库用户名
    "password": "282532",   # 数据库密码
    "database": "osm_road", # 要使用的数据库（需提前创建，如CREATE DATABASE osm_road;）
    "charset": "utf8mb4"    # 字符集，支持中文/emoji
}
# 日志文件路径：记录不合规文件/异常信息
LOG_FILE = os.path.join(ROOT_DIR, "data_process_log.log")
# 目标MySQL表名
TABLE_NAME = "city_road_pano"
# -------------------------- 2. 省份-城市字典映射（核心！可按需补充/修改）--------------------------
# 格式：{城市文件夹名: 省份名}，覆盖你的文件夹名（如杭州市、北京市、澳门特别行政区）
with open(MAP_JSON_PATH, "r", encoding="utf-8") as f:
    PROVINCE_CITY_MAP = json.load(f)
            
# -------------------------- 3. 日志配置（记录错误/跳过信息）--------------------------
def init_logger() -> logging.Logger:
    """初始化日志器：同时输出到控制台+本地文件"""
    logger = logging.getLogger("osm_road_process")
    logger.setLevel(logging.INFO)
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    # 格式：时间 - 级别 - 信息
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    # 文件处理器：写入本地log
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)
    # 控制台处理器：实时查看
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

# -------------------------- 4. MySQL工具（连接、建表）--------------------------
def get_mysql_conn() -> pymysql.connections.Connection:
    """获取MySQL连接，自动检测并创建数据库，失败则抛出异常并记录日志"""
    try:
        # 先临时连接MySQL（不指定数据库），用于创建数据库
        temp_conn = pymysql.connect(
            host=MYSQL_CONFIG["host"],
            user=MYSQL_CONFIG["user"],
            password=MYSQL_CONFIG["password"],
            charset=MYSQL_CONFIG["charset"]
        )
        with temp_conn.cursor() as cursor:
            # 自动创建数据库（IF NOT EXISTS：存在则不重复创建，避免报错）
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']}")
        temp_conn.close()
        # 再连接指定的数据库
        conn = pymysql.connect(**MYSQL_CONFIG)
        logger.info(f"MySQL数据库{MYSQL_CONFIG['database']}创建/检测成功，连接成功！")
        return conn
    except OperationalError as e:
        logger.error(f"MySQL连接失败：请检查host/user/password是否正确，错误信息：{e}")
        raise SystemExit(1)  # 连接失败直接退出程序

def create_mysql_table(conn: pymysql.connections.Connection):
    """创建MySQL表：字段为id(自增)、province(省份)、city(城市)、longitude、latitude、pano_id、year、month"""
    create_sql = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        id INT PRIMARY KEY AUTO_INCREMENT COMMENT '数据库自增主键',
        province VARCHAR(50) NOT NULL COMMENT '省份名称',
        city VARCHAR(50) NOT NULL COMMENT '城市名称',
        longitude FLOAT(15, 12) NOT NULL COMMENT '经度',
        latitude FLOAT(15, 12) NOT NULL COMMENT '纬度',
        pano_id VARCHAR(50) NOT NULL COMMENT '全景ID',
        year INT NOT NULL COMMENT '年份',
        month INT NOT NULL COMMENT '月份',
        INDEX idx_city (city),
        INDEX idx_pano_id (pano_id),
        INDEX idx_year_month (year, month)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='全国城市道路全景数据';
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(create_sql)
        conn.commit()
        logger.info(f"MySQL表{TABLE_NAME}创建/检查成功！")
    except ProgrammingError as e:
        logger.error(f"创建表失败，错误信息：{e}")
        conn.rollback()
        raise

# -------------------------- 5. 数据处理核心函数 --------------------------
def check_csv_format(df: pd.DataFrame) -> bool:
    """校验CSV列格式是否符合要求：必须包含['longitude','latitude','pano_id','year','month']"""
    required_cols = {"longitude", "latitude", "pano_id", "year", "month"}
    actual_cols = set(df.columns)
    return required_cols.issubset(actual_cols)

def get_city_csv_path(city_dir: str) -> str | None:
    """获取城市文件夹下唯一的CSV文件路径，无CSV/多个CSV则返回None"""
    csv_files = [f for f in os.listdir(city_dir) if f.endswith(".csv")]
    if len(csv_files) == 1:
        return os.path.join(city_dir, csv_files[0])
    return None

def process_city_data(city_name: str, city_dir: str, conn: pymysql.connections.Connection):
    """处理单个城市数据：读取CSV→校验格式→补充省份城市→写入MySQL"""
    # 1. 检查城市是否在省份映射中
    if city_name not in PROVINCE_CITY_MAP:
        logger.warning(f"跳过{city_name}：未在省份-城市映射字典中配置，需补充后重新处理")
        return
    province_name = PROVINCE_CITY_MAP[city_name]
    
    # 2. 获取城市文件夹下的CSV文件
    csv_path = get_city_csv_path(city_dir)
    if not csv_path:
        logger.error(f"跳过{city_name}：文件夹下无CSV文件/存在多个CSV文件，非唯一")
        return
    
    # 3. 读取CSV并处理异常
    try:
        df = pd.read_csv(csv_path, encoding="utf-8")  # 若CSV是gbk编码，替换为encoding="gbk"
    except Exception as e:
        logger.error(f"读取{city_name}的CSV失败（路径：{csv_path}），错误信息：{e}")
        return
    
    # 4. 校验CSV列格式
    if not check_csv_format(df):
        logger.error(f"跳过{city_name}：CSV列格式不合规，要求包含{['longitude','latitude','pano_id','year','month']}，实际列：{list(df.columns)}")
        return
    
    # 5. 筛选有效列并补充省份、城市字段
    df_processed = df[["longitude", "latitude", "pano_id", "year", "month"]].copy()
    df_processed["province"] = province_name
    df_processed["city"] = city_name
    # 调整列顺序：匹配MySQL表（province, city, longitude, latitude, pano_id, year, month）
    df_processed = df_processed[["province", "city", "longitude", "latitude", "pano_id", "year", "month"]]
    # 去除空值（避免入库失败）
    df_processed = df_processed.dropna()
    if df_processed.empty:
        logger.warning(f"跳过{city_name}：CSV有效数据为空（已去除空值）")
        return
    
    # 6. 批量写入MySQL（高效，比逐行插入快）
    try:
        # 构造插入SQL
        cols = ",".join(df_processed.columns)
        placeholders = ",".join(["%s"] * len(df_processed.columns))
        insert_sql = f"INSERT INTO {TABLE_NAME} ({cols}) VALUES ({placeholders})"
        # 转换为元组列表（pymysql要求的格式）
        data_tuples = [tuple(row) for row in df_processed.values]
        # 执行批量插入
        with conn.cursor() as cursor:
            cursor.executemany(insert_sql, data_tuples)
        conn.commit()
        logger.info(f"成功处理{city_name}：入库{len(df_processed)}条数据，CSV路径：{csv_path}")
    except Exception as e:
        logger.error(f"写入{city_name}数据到MySQL失败，错误信息：{e}")
        conn.rollback()

# -------------------------- 6. 主函数（入口）--------------------------
def main():
    global logger
    # 初始化日志
    logger = init_logger()
    # 检查根路径是否存在
    if not os.path.isdir(ROOT_DIR):
        logger.error(f"根路径不存在：{ROOT_DIR}，请检查路径是否正确！")
        return
    # 获取MySQL连接并创建表
    conn = get_mysql_conn()
    create_mysql_table(conn)
    # 遍历根路径下的所有城市文件夹
    city_folders = [f for f in os.listdir(ROOT_DIR) if os.path.isdir(os.path.join(ROOT_DIR, f))]
    if not city_folders:
        logger.warning(f"根路径下无任何城市文件夹：{ROOT_DIR}")
        conn.close()
        return
    logger.info(f"共发现{len(city_folders)}个城市文件夹，开始逐一生成处理...")
    # 处理每个城市
    for city_name in city_folders:
        city_dir = os.path.join(ROOT_DIR, city_name)
        process_city_data(city_name, city_dir, conn)
    # 关闭连接
    conn.close()
    logger.info("所有城市数据处理完成！日志文件路径：%s", LOG_FILE)

if __name__ == "__main__":
    main()