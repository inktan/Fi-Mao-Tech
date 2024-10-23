import pandas as pd  
  
# 读取CSV文件  
csv01 = pd.read_csv(r'e:\work\sv_YJ_20240924\points\adjusted_clip_params3_20241020_060233.csv')  
csv02 = pd.read_csv(r'e:\work\sv_YJ_20240924\points\los_angeles_panoid_only_latest_year.csv')  
  
# 重命名列以匹配条件  
csv01_renamed = csv01.rename(columns={'osm_id': 'building_id_ori', 'categories': 'categories_ori'})  
  
# 合并数据，使用内连接（inner join）来找到匹配的行  
merged_data = pd.merge(csv01_renamed, csv02[['building_id_ori', 'categories_ori', 'pano_id']],   
                       on=['building_id_ori', 'categories_ori'], how='inner')  

print(merged_data)
merged_data.to_csv('e:\work\sv_YJ_20240924\points\merged_file_adjusted.csv', index=False)





