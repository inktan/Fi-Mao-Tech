import geopandas as gpd
from shapely.geometry import Polygon

import pandas as pd
from tqdm import tqdm
import os

roots = []
shp_names = []
shp_paths = []
accepted_formats = (".shp")
for root, dirs, files in os.walk(r'E:\work\sv_hukejia\sv\handle\points01_panoid03'):
    for file in files:
        if file.endswith(accepted_formats):
            roots.append(root)
            shp_names.append(file)
            file_path = os.path.join(root, file)
            shp_paths.append(file_path)

shp_paths =[r'e:\work\sv_xiufenganning\地理数据\grid_points_with_attributes.shp']

# for shp_path in tqdm(shp_paths):
for shp_path in shp_paths:
    gdf = gpd.read_file(shp_path)

    # 2. 验证是否为点数据
    if not all(gdf.geometry.type == 'Point'):
        print("警告：输入文件不全是点要素，只有点要素会被处理")

    # 3. 提取点坐标到新列
    gdf['longitude'] = gdf.geometry.x  # 经度
    gdf['latitude'] = gdf.geometry.y  # 纬度

    # 4. 删除几何列（因为CSV无法存储几何信息）
    df = pd.DataFrame(gdf.drop(columns='geometry'))

    # 5. 保存为CSV
    output_csv = shp_path.replace('.shp', '.csv')  # 生成与输入同名的CSV文件
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')  # 使用utf-8-sig编码支持中文

    print(f"转换完成！结果已保存到: {output_csv}")
    print(f"共转换了 {len(df)} 个点")




