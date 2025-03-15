import geopandas as gpd
import pandas as pd
import os

def merge_csv_to_shp(shp_file, csv_file, output_file):
    """
    将 CSV 数据基于 "FID" 列合并到 SHP 文件中，并保存为新的 SHP 文件。

    参数:
        shp_file (str): SHP 文件的路径。
        csv_file (str): CSV 文件的路径。
        output_file (str): 输出 SHP 文件的路径。
    """

    try:
        # 读取 SHP 文件
        gdf = gpd.read_file(shp_file)

        # 添加自增的 "id" 列
        gdf["FID"] = range(len(gdf))


        # 读取 CSV 文件
        df = pd.read_csv(csv_file)

        # 检查 "FID" 列是否存在
        if "FID" not in gdf.columns or "FID" not in df.columns:
            print("错误: SHP 文件或 CSV 文件中不存在 'FID' 列。")
            return

        # 将 "FID" 列转换为相同的数据类型，以便进行合并
        gdf["FID"] = gdf["FID"].astype(df["FID"].dtype)

        # 基于 "FID" 列合并 DataFrame 和 GeoDataFrame
        merged_gdf = gdf.merge(df, on="FID", how="left")

        # 保存为新的 SHP 文件
        merged_gdf.to_file(output_file)

        print(f"成功: 已将 CSV 数据合并到 SHP 文件，并保存到 '{output_file}'。")

    except FileNotFoundError:
        print("错误: SHP 文件或 CSV 文件未找到。")
    except Exception as e:
        print(f"发生错误: {e}")

# 示例用法
shp_file = r"e:\work\sv_juanjuanmao\20250308\八条路线\merged_output.shp"  # 替换为你的 SHP 文件路径
csv_file = r"e:\work\sv_juanjuanmao\20250308\吸引力数据\attractive_force.csv"  # 替换为你的 CSV 文件路径
output_file = r"e:\work\sv_juanjuanmao\20250308\吸引力数据\attractive_force.shp"  # 替换为你的输出 SHP 文件路径

merge_csv_to_shp(shp_file, csv_file, output_file)