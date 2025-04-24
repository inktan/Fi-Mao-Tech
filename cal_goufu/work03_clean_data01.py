import geopandas as gpd
from tqdm import tqdm  # 用于显示进度条

columns = [
    'Join_Count', 
    'NEAR_DIST','dem','density','landcover','ylight',
    'ndvi','podu','population','poxiang','rain',
    'road2','temper','densitywa','lengthwa'
    ]


years = ['98','99','00',
'01','02','03','04','05','06','07','08','09','10',
'11','12','13','14','15','16','17','18','19','20',
'22','23',]

for year in years:
    print(year)

    src_file = f'e:\\work\\sv_goufu\\MLP\\year{year}\\year{year}.shp'

    # 读取数据源文件
    src_gdf = gpd.read_file(src_file)

    # 创建筛选条件 - 首先确保Join_Count > 0
    filter_condition = (src_gdf['dem'] > -9999)

    # 添加其他列的筛选条件（都大于-99999）
    for col in columns[1:]:  # 跳过第一个Join_Count列
        filter_condition &= (src_gdf[col] > -9999)

    # 应用筛选条件
    filtered_gdf = src_gdf[filter_condition]

    # 输出结果信息
    print(f"原始记录数: {len(src_gdf)}")
    print(f"筛选后记录数: {len(filtered_gdf)}")
    print(f"筛选掉记录数: {len(src_gdf) - len(filtered_gdf)}")

    # 保存结果（可选）
    output_file = src_file.replace('.shp', '_valid_data.shp')
    filtered_gdf.to_file(output_file)
    print(f"筛选结果已保存到: {output_file}")