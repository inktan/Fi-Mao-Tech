import os
import logging
import pandas as pd
import json

# -------------------------- 基础配置（仅需确认2个路径，其余默认）--------------------------
ROOT_DIR = r"F:\osm\2025年8月份道路矢量数据\分城市的道路数据_50m_svinfo_csv"  # 城市文件夹根路径
MAP_JSON_PATH = r"D:\Users\mslne\Documents\GitHub\Fi-Mao-Tech\mysql\PROVINCE_CITY_MAP.json"  # 省份映射JSON路径
LOG_FILE = os.path.join(ROOT_DIR, "data_process_log.log")  # 日志文件路径
RESULT_CSV_PATH = os.path.join(ROOT_DIR, "城市50m数据汇总.csv")  # 最终汇总CSV保存路径
# ------------------------------------------------------------------------------------------

# 初始化省份-城市映射（读取JSON）
with open(MAP_JSON_PATH, "r", encoding="utf-8") as f:
    PROVINCE_CITY_MAP = json.load(f)

# 初始化日志（保留控制台+本地文件，方便排查问题）
def init_logger():
    logger = logging.getLogger("city_count_process")
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return logger
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    # 文件日志
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)
    # 控制台日志
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

# 获取城市文件夹下唯一的CSV文件路径
def get_city_csv_path(city_dir):
    csv_files = [f for f in os.listdir(city_dir) if f.endswith(".csv")]
    return os.path.join(city_dir, csv_files[0]) if len(csv_files) == 1 else None

# 处理单个城市：读取CSV→统计index唯一值数量
def process_city(city_name, city_dir, logger):
    # 1. 检查是否在省份映射中
    if city_name not in PROVINCE_CITY_MAP:
        logger.warning(f"跳过{city_name}：未在省份-城市映射中配置")
        return None
    province = PROVINCE_CITY_MAP[city_name]
    
    # 2. 获取唯一CSV文件
    csv_path = get_city_csv_path(city_dir)
    if not csv_path:
        logger.error(f"跳过{city_name}：文件夹下无CSV/多个CSV，非唯一")
        return None
    
    # 3. 读取CSV并统计index列唯一值数量
    try:
        df = pd.read_csv(csv_path, encoding="utf-8")  # 编码不对则改gbk
        # 校验是否有index列（无则跳过）
        if "index" not in df.columns:
            logger.error(f"跳过{city_name}：CSV无index列，无法统计")
            return None
        # 计算唯一index数量 → count_50
        count_50 = df["index"].nunique()
        logger.info(f"成功处理{city_name}：唯一index数={count_50}")
        return {"province": province, "city": city_name, "count_50": count_50}
    except Exception as e:
        logger.error(f"处理{city_name}失败，错误：{e}")
        return None

# 主函数：遍历所有城市→汇总数据→生成CSV
def main():
    logger = init_logger()
    # 校验根路径是否存在
    if not os.path.isdir(ROOT_DIR):
        logger.error(f"根路径不存在：{ROOT_DIR}，请检查！")
        return
    
    # 存储所有城市的统计结果
    result_list = []
    # 遍历根路径下所有城市文件夹
    city_folders = [f for f in os.listdir(ROOT_DIR) if os.path.isdir(os.path.join(ROOT_DIR, f))]
    if not city_folders:
        logger.warning("根路径下无任何城市文件夹！")
        return
    
    logger.info(f"共发现{len(city_folders)}个城市文件夹，开始统计...")
    # 逐个处理城市
    for city_name in city_folders:
        city_dir = os.path.join(ROOT_DIR, city_name)
        city_data = process_city(city_name, city_dir, logger)
        if city_data:  # 处理成功则加入结果列表
            result_list.append(city_data)
    
    # 生成最终汇总CSV（添加自增id，按指定列排序）
    if result_list:
        result_df = pd.DataFrame(result_list)
        result_df.insert(0, "id", range(1, len(result_df)+1))  # 插入自增id列（从1开始）
        result_df = result_df[["id", "province", "city", "count_50"]]  # 固定列顺序
        result_df.to_csv(RESULT_CSV_PATH, index=False, encoding="utf-8-sig")  # utf-8-sig解决中文乱码
        logger.info(f"所有数据处理完成！汇总CSV已保存至：{RESULT_CSV_PATH}，共统计{len(result_df)}个城市")
    else:
        logger.warning("无有效城市数据，未生成汇总CSV！")

if __name__ == "__main__":
    main()