import pandas as pd
import geopandas as gpd
import pandas as pd

# 读取文件
shp_data = gpd.read_file(r'e:\work\sv_xiufenganning\20250819\街景视觉-类别情感.shp')
# 读取csv文件
# df = pd.read_csv(r'f:\立方数据\2025年道路数据\【立方数据学社】台湾省\台湾省_15m_unique01.csv')



# 修改列名
shp_data.rename(columns={'地址_x': '地址'}, inplace=True) 
output_path = r'e:\work\sv_xiufenganning\20250819\街景视觉-类别情感01.shp'
shp_data.to_file(output_path, driver='ESRI Shapefile', encoding='utf-8')

# 保存修改后的DataFrame到新的csv文件
# df.to_csv(r'f:\立方数据\2025年道路数据\【立方数据学社】台湾省\台湾省_15m_unique01.csv', index=False)