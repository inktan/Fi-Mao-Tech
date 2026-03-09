import json
import geopandas as gpd
import matplotlib.pyplot as plt

# 1. 定义文件路径
# 使用 r 前缀避免反斜杠转义问题
file_path = r"e:\work\sv_zhoujunling\20260209\OSMB-13ca4e6f72ce0d9773fe5206137002939b07a485.geojson"

def plot_custom_geojson(path):
    try:
        # 2. 读取原始 JSON 文件
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 3. 提取嵌套的 features
        # 你的格式是 {"features": {"features": [...]}}
        if "features" in data and isinstance(data["features"], dict):
            inner_features = data["features"]["features"]
        else:
            inner_features = data["features"]

        # 4. 转换为 GeoDataFrame
        gdf = gpd.GeoDataFrame.from_features(inner_features)

        # 5. 绘图设置
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # 绘制所有 Polygon
        # facecolor: 填充颜色, edgecolor: 边框颜色 (类似 Google Maps 的红色线条)
        gdf.plot(ax=ax, alpha=0.3, facecolor='royalblue', edgecolor='red', linewidth=1.5)

        # 6. 添加标注（如果属性中有 name 列）
        if 'name' in gdf.columns:
            for idx, row in gdf.iterrows():
                if row['geometry'] and row['geometry'].is_valid:
                    centroid = row['geometry'].centroid
                    # 只有当名字不为空时才标注
                    if row['name'] and str(row['name']) != 'nan':
                        ax.text(centroid.x, centroid.y, str(row['name']), 
                                fontsize=9, ha='center', color='darkred', fontfamily='SimHei')

        # 图形美化
        ax.set_title("Polygon Geometry Visualization", fontsize=14)
        ax.set_xlabel("Longitude (WGS84)")
        ax.set_ylabel("Latitude (WGS84)")
        plt.grid(True, linestyle=':', alpha=0.5)
        
        # 自动调整比例
        plt.tight_layout()
        plt.show()

    except FileNotFoundError:
        print(f"错误：找不到文件，请检查路径是否正确：{path}")
    except Exception as e:
        print(f"发生错误：{e}")

# 执行函数
plot_custom_geojson(file_path)