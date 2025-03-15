import geopandas as gpd
import os

def calculate_line_length(shp_file):
    try:
        gdf = gpd.read_file(shp_file)
        gdf_utm = gdf.to_crs(epsg=32633)
        gdf['length_meters'] = gdf_utm.geometry.length
        total_length = gdf['length_meters'].sum()
        print(shp_file, total_length)

    except FileNotFoundError:
        print(f"错误: SHP 文件 '{shp_file}' 未找到。")
    except Exception as e:
        print(f"发生错误: {e}")

def process_shp_files_in_directory(directory):
    try:
        for filename in os.listdir(directory):
            if filename.endswith(".shp"):
                file_path = os.path.join(directory, filename)
                calculate_line_length(file_path)

    except FileNotFoundError:
        print(f"错误: 目录 '{directory}' 未找到。")
    except Exception as e:
        print(f"发生错误: {e}")

directory = r"E:\work\sv_juanjuanmao\20250308\八条路线"  # 替换为你的 SHP 文件所在的目录
process_shp_files_in_directory(directory)