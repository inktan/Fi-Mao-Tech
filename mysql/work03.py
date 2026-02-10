import os
import logging
import pandas as pd
import json

# -------------------------- 基础配置（仅需确认2个路径）--------------------------
ROOT_DIR = r"F:\osm\2025年8月份道路矢量数据\分城市的道路数据_50m_svinfo_csv"
MAP_JSON_PATH = r"D:\Users\mslne\Documents\GitHub\Fi-Mao-Tech\mysql\PROVINCE_CITY_MAP.json"
LOG_FILE = os.path.join(ROOT_DIR, "data_process_log.log")
RESULT_CSV_PATH = os.path.join(ROOT_DIR, "各个城市可下载街景点数据统计汇总.csv")
# ------------------------------------------------------------------------------------------

# 读取省份-城市映射JSON
with open(MAP_JSON_PATH, "r", encoding="utf-8") as f:
    PROVINCE_CITY_MAP = json.load(f)

# 初始化日志（控制台+本地文件，截断超长错误信息）
def init_logger():
    logger = logging.getLogger("city_count_process")
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return logger
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    console_handler = logging.StreamHandler()
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

# 获取城市文件夹下唯一CSV文件路径
def get_city_csv_path(city_dir):
    csv_files = [f for f in os.listdir(city_dir) if f.endswith(".csv")]
    return os.path.join(city_dir, csv_files[0]) if len(csv_files) == 1 else None

# 通用最值统计函数（抽离公共逻辑，避免year/month代码冗余）
def get_col_min_max(series):
    """
    计算列的最值，兼容数值/字符串，返回字符串类型结果
    :param series: 预处理后的列数据（已过滤空值、去空格）
    :return: min_str, max_str
    """
    try:
        # 尝试转数值型，转成后取最值（避免10<2的字符串排序问题）
        series_num = pd.to_numeric(series)
        min_val = series_num.min()
        max_val = series_num.max()
        # 转整数再转字符串，避免1.0、12.0这类浮点格式
        return str(int(min_val)), str(int(max_val))
    except:
        # 转数值失败则按字符串自然排序取最值
        return series.min(), series.max()

# 处理单个城市：核心优化-替换year/month_unique分隔符为分号，适配Excel
def process_city(city_name, city_dir, logger):
    # 1. 校验省份映射
    if city_name not in PROVINCE_CITY_MAP:
        logger.warning(f"跳过{city_name}：未在省份-城市映射中配置")
        return None
    province = PROVINCE_CITY_MAP[city_name]
    
    # 2. 校验CSV唯一性
    csv_path = get_city_csv_path(city_dir)
    if not csv_path:
        logger.error(f"跳过{city_name}：文件夹下无CSV/多个CSV，非唯一")
        return None
    
    # 3. 读取CSV并多维度统计（核心：分隔符改为分号，解决Excel乱码）
    try:
        df = pd.read_csv(csv_path, encoding="utf-8")  # 编码错误直接改gbk即可
        # 必选列校验：index+year+month缺一不可，缺少直接跳过
        required_cols = ["index", "year", "month"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            logger.error(f"跳过{city_name}：CSV缺少必选列→{missing_cols}，无法完成统计")
            return None
        
        # 基础统计：index列唯一值数量（原count_50）
        count_50 = df["index"].nunique()

        # -------------------------- Year列统计（核心改：unique用分号分隔）--------------------------
        year_series = df["year"].astype(str)
        year_series = year_series[year_series != ""]
        if year_series.empty:
            year_min = year_max = "无"
            year_unique_str = "无"
            year_count_str = "无"
        else:
            year_min, year_max = get_col_min_max(year_series)
            year_count = year_series.value_counts().sort_index()
            # 关键修改：将逗号,改为分号;，避免Excel识别为数字分隔符
            year_unique_str = ";".join(year_count.index.tolist())
            year_count_str = ";".join([f"{y}:{c}" for y, c in year_count.items()])

        # -------------------------- Month列统计（核心改：unique用分号分隔）--------------------------
        month_series = df["month"].astype(str)
        month_series = month_series[month_series != ""]
        if month_series.empty:
            # 无有效month数据时统一标注为"无"，和year格式一致
            month_min = month_max = "无"
            month_unique_str = "无"
            month_count_str = "无"
        else:
            # 调用通用函数取最值，兼容1/01/"1"/"01"等格式
            month_min, month_max = get_col_min_max(month_series)
            # 按月份升序统计数量
            month_count = month_series.value_counts().sort_index()
            # 关键修改：将逗号,改为分号;，适配Excel
            month_unique_str = ";".join(month_count.index.tolist())
            month_count_str = ";".join([f"{m}:{c}" for m, c in month_count.items()])
        
        # 控制台打印详细统计结果，实时查看处理进度
        logger.info(
            f"成功处理{city_name} → 唯一index：{count_50} | "
            f"年份：{year_min}~{year_max} 唯一值：{year_unique_str} | 计数：{year_count_str} | "
            f"月份：{month_min}~{month_max} 唯一值：{month_unique_str} | 计数：{month_count_str}"
        )
        # 返回所有统计字段
        return {
            "province": province,
            "city": city_name,
            "count_50": count_50,
            # Year相关列（4个，分隔符改分号）
            "year_min": year_min,
            "year_max": year_max,
            "year_unique": year_unique_str,
            "year_count": year_count_str,
            # Month相关列（4个，分隔符改分号）
            "month_min": month_min,
            "month_max": month_max,
            "month_unique": month_unique_str,
            "month_count": month_count_str
        }
    except Exception as e:
        # 截断超长错误信息，避免日志冗余
        logger.error(f"处理{city_name}失败，错误详情：{str(e)[:100]}")
        return None

# 主函数：遍历所有城市→生成11列汇总CSV→固定列顺序
def main():
    logger = init_logger()
    # 根路径有效性校验
    if not os.path.isdir(ROOT_DIR):
        logger.error(f"程序终止：城市文件夹根路径不存在→{ROOT_DIR}，请检查路径是否正确！")
        return
    
    result_list = []
    # 遍历根路径下所有城市/区域文件夹（仅保留文件夹，过滤文件）
    city_folders = [f for f in os.listdir(ROOT_DIR) if os.path.isdir(os.path.join(ROOT_DIR, f))]
    if not city_folders:
        logger.warning("程序终止：根路径下未发现任何城市/区域文件夹，无数据可统计！")
        return
    
    # 批量处理所有城市
    logger.info(f"开始统计 → 共发现{len(city_folders)}个城市/区域文件夹，逐一生成统计数据...")
    for city_name in city_folders:
        city_dir = os.path.join(ROOT_DIR, city_name)
        city_stat_data = process_city(city_name, city_dir, logger)
        if city_stat_data:
            result_list.append(city_stat_data)
    
    # 生成最终汇总CSV，保证列顺序固定
    if result_list:
        result_df = pd.DataFrame(result_list)
        # 插入自增id列（从1开始，仅对有效统计城市编号）
        result_df.insert(0, "id", range(1, len(result_df) + 1))
        # 固定11列顺序，year/month统计完全对称
        final_fixed_cols = [
            "id", "province", "city", "count_50",
            # Year统计4列（分隔符改分号）
            "year_min", "year_max", "year_unique", "year_count",
            # Month统计4列（分隔符改分号）
            "month_min", "month_max", "month_unique", "month_count"
        ]
        result_df = result_df[final_fixed_cols]
        # 写入CSV：utf-8-sig彻底解决中文乱码，index=False不生成多余索引
        result_df.to_csv(RESULT_CSV_PATH, index=False, encoding="utf-8-sig")
        # 日志打印最终统计结果，提示分隔符修改
        logger.info(
            f"\n✅ 所有数据统计完成！\n📁 汇总CSV保存路径：{RESULT_CSV_PATH}\n"
            f"📊 统计结果：有效城市/区域共{len(result_df)}个 | 汇总列共{len(final_fixed_cols)}列\n"
            f"💡 关键优化：year_unique/month_unique分隔符改为分号;，解决Excel数字识别乱码问题"
        )
    else:
        logger.warning("⚠️  无任何有效城市/区域数据，未生成汇总CSV文件！")

if __name__ == "__main__":
    main()