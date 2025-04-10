import geopandas as gpd
import os

# 鸟类数据
# 要创建的年份范围 (1998-2023)
start_year = 1998
end_year = 2023

shp_file_paths=[]
for year in range(start_year, end_year + 1):
    # 格式化年份为两位数字 (98, 99, 00, 01, ..., 23)
    year_str = f"{str(year)[2:]}"
    folder_path = f'e:\\work\\sv_goufu\\datatrain\\bird02\\tongji\\tj{year_str}.shp'
    shp_file_paths.append(folder_path)
    
# shp_file_paths=[
#     r'e:\work\sv_goufu\datatrain\bird02\tongji\tj22.shp',
#     r'e:\work\sv_goufu\datatrain\bird02\tongji\tj23.shp',
# ]

for file_path in shp_file_paths:
    print(f"Processing file: {file_path}")
    shp_file = gpd.read_file(file_path)  # 替换为你的SHP文件路径
    # element = shp_file.iloc[4, 1] 
    # element = shp_file.head()
    filtered_data = shp_file[shp_file['Join_Count'] > 0]
    print(filtered_data.shape)
    # print(filtered_data.crs)
    # print(filtered_data.columns)
    # print(filtered_data)

# 城市环境因子作为预测变量

shp_file_paths=[
    r'e:\work\sv_goufu\datatrain\coastline\点数据\shcoastline.shp',
]
# for file_path in shp_file_paths:
#     coastline_shp_file = gpd.read_file(file_path)
#     print(f"Processing file: {file_path}")

#     filtered_data = coastline_shp_file[coastline_shp_file['NEAR_DIST'] > -9999]
#     print(filtered_data.shape)
#     print(filtered_data.crs)
#     print(filtered_data.head())

shp_file_paths=[
    r'e:\work\sv_goufu\datatrain\dem\点数据\dem.shp',
]
# for file_path in shp_file_paths:
#     dem_shp_file = gpd.read_file(file_path)
#     print(f"Processing file: {file_path}")

#     filtered_data = dem_shp_file[dem_shp_file['dem'] > -9999]
#     print(filtered_data.shape)
#     print(filtered_data.crs)

# 归一化植被指数 (NDVI):  反映城市绿地植被覆盖度。

shp_file_paths=[
    r'E:\work\sv_goufu\datatrain\green\xiangjiao\shgren00.shp',
    r'E:\work\sv_goufu\datatrain\green\xiangjiao\shgren05.shp',
    r'E:\work\sv_goufu\datatrain\green\xiangjiao\shgren10.shp',
    r'E:\work\sv_goufu\datatrain\green\xiangjiao\shgren15.shp',
    r'E:\work\sv_goufu\datatrain\green\xiangjiao\shgren19.shp',
    r'E:\work\sv_goufu\datatrain\green\xiangjiao\shgren22.shp',
]

# for file_path in shp_file_paths:
#     green_shp_file = gpd.read_file(file_path)
#     print(f"Processing file: {file_path}")

#     filtered_data = green_shp_file[green_shp_file['areagr'] > -9999]
#     print(filtered_data.shape)
#     print(filtered_data.crs)

shp_file_paths=[
    r'E:\work\sv_goufu\datatrain\landcoverpre\点数据\sh22.shp',
    r'E:\work\sv_goufu\datatrain\landcoverpre\点数据\sh19.shp',
    r'E:\work\sv_goufu\datatrain\landcoverpre\点数据\sh15.shp',
    r'E:\work\sv_goufu\datatrain\landcoverpre\点数据\sh10.shp',
    r'E:\work\sv_goufu\datatrain\landcoverpre\点数据\sh05.shp',
    r'E:\work\sv_goufu\datatrain\landcoverpre\点数据\sh00.shp',
]
# for file_path in shp_file_paths:
#     landcoverpre_shp_file = gpd.read_file(file_path)
#     print(f"Processing file: {file_path}")

#     filtered_data = landcoverpre_shp_file[landcoverpre_shp_file['RASTERVALU'] > -9999]
#     print(filtered_data.shape)
#     print(filtered_data.crs)

shp_file_paths=[
r'E:\work\sv_goufu\datatrain\lightyear\点数据\ylight00.shp',
r'E:\work\sv_goufu\datatrain\lightyear\点数据\ylight05.shp',
r'E:\work\sv_goufu\datatrain\lightyear\点数据\ylight10.shp',
r'E:\work\sv_goufu\datatrain\lightyear\点数据\ylight15.shp',
r'E:\work\sv_goufu\datatrain\lightyear\点数据\ylight20.shp',
r'E:\work\sv_goufu\datatrain\lightyear\点数据\ylight23.shp',
]
# for file_path in shp_file_paths:
#     lightyear_file_file  = gpd.read_file(file_path)
#     print(f"Processing file: {file_path}")

#     filtered_data = lightyear_file_file [lightyear_file_file ['ylight'] > -9999]
#     print(filtered_data.shape)
#     print(filtered_data.crs)

shp_file_paths=[
r'E:\work\sv_goufu\datatrain\ndvi\点数据\00nd点.shp',
r'E:\work\sv_goufu\datatrain\ndvi\点数据\05nd点.shp',
r'E:\work\sv_goufu\datatrain\ndvi\点数据\10nd点.shp',
r'E:\work\sv_goufu\datatrain\ndvi\点数据\15nd点.shp',
r'E:\work\sv_goufu\datatrain\ndvi\点数据\20nd点.shp',
r'E:\work\sv_goufu\datatrain\ndvi\点数据\24nd点.shp',
]
# for file_path in shp_file_paths:
#     ndvi_file_file  = gpd.read_file(file_path)
#     print(f"Processing file: {file_path}")

#     filtered_data = ndvi_file_file [ndvi_file_file ['ndvi'] > -9999]
#     print(filtered_data.shape)
#     print(filtered_data.crs)

shp_file_paths=[
    r'e:\work\sv_goufu\datatrain\podu\点数据\shpod.shp',
]
# for file_path in shp_file_paths:
#     podu_file_file  = gpd.read_file(file_path)
#     print(f"Processing file: {file_path}")

#     filtered_data = podu_file_file [podu_file_file ['podu'] > -9999]
#     print(filtered_data.shape)
#     print(filtered_data.crs)

shp_file_paths=[
r'E:\work\sv_goufu\datatrain\population\点数据\00shpop.shp',
r'E:\work\sv_goufu\datatrain\population\点数据\05shpop.shp',
r'E:\work\sv_goufu\datatrain\population\点数据\10shpop.shp',
r'E:\work\sv_goufu\datatrain\population\点数据\15shpop.shp',
r'E:\work\sv_goufu\datatrain\population\点数据\20shpop.shp',
r'E:\work\sv_goufu\datatrain\population\点数据\23shpop.shp',
]
# for file_path in shp_file_paths:
#     population_file_file  = gpd.read_file(file_path)
#     print(f"Processing file: {file_path}")

#     filtered_data = population_file_file [population_file_file ['population'] > -9999]
#     print(filtered_data.shape)
#     print(filtered_data.crs)

shp_file_paths=[
    r'e:\work\sv_goufu\datatrain\poxiang\点数据\shpoxiang.shp',
]

# for file_path in shp_file_paths:
#     poxiang_shp_file = gpd.read_file(file_path)
#     print(f"Processing file: {file_path}")

#     filtered_data = poxiang_shp_file[poxiang_shp_file['poxiang'] > -9999]
#     print(filtered_data.shape)
#     print(filtered_data.crs)

shp_file_paths=[
    r'E:\work\sv_goufu\datatrain\rain\点数据\00.shp',
    r'E:\work\sv_goufu\datatrain\rain\点数据\05.shp',
    r'E:\work\sv_goufu\datatrain\rain\点数据\10.shp',
    r'E:\work\sv_goufu\datatrain\rain\点数据\15.shp',
    r'E:\work\sv_goufu\datatrain\rain\点数据\20.shp',
    r'E:\work\sv_goufu\datatrain\rain\点数据\23.shp',
]

# for file_path in shp_file_paths:
#     AP_file_file  = gpd.read_file(file_path)
#     print(f"Processing file: {file_path}")

#     filtered_data = AP_file_file [AP_file_file ['podu'] > -9999]
#     print(filtered_data.shape)
#     print(filtered_data.crs)

shp_file_paths=[
r'E:\work\sv_goufu\datatrain\road2\点数据\road15.shp',
r'E:\work\sv_goufu\datatrain\road2\点数据\road20.shp',
r'E:\work\sv_goufu\datatrain\road2\点数据\road25.shp',
]
# for file_path in shp_file_paths:
#     road2_file_file  = gpd.read_file(file_path)
#     print(f"Processing file: {file_path}")

#     filtered_data = road2_file_file [road2_file_file ['RASTERVALU'] > -9999]
#     print(filtered_data.shape)
#     print(filtered_data.crs)

shp_file_paths=[
    r'e:\work\sv_goufu\datatrain\temper\点数据\00.shp',
    r'e:\work\sv_goufu\datatrain\temper\点数据\2.shp',
    r'e:\work\sv_goufu\datatrain\temper\点数据\05.shp',
    r'e:\work\sv_goufu\datatrain\temper\点数据\10.shp',
    r'e:\work\sv_goufu\datatrain\temper\点数据\15.shp',
    r'e:\work\sv_goufu\datatrain\temper\点数据\20.shp',
]
# for file_path in shp_file_paths:
    # temper_shp_file = gpd.read_file(file_path)
    # print(f"Processing file: {file_path}")

    # filtered_data = temper_shp_file[temper_shp_file['temper'] > 0]
    # print(filtered_data.shape)
    # print(filtered_data.crs)

shp_file_paths=[
    r'E:\work\sv_goufu\datatrain\water\density\shwa00.shp',
    r'E:\work\sv_goufu\datatrain\water\density\shwa05.shp',
    r'E:\work\sv_goufu\datatrain\water\density\shwa10.shp',
    r'E:\work\sv_goufu\datatrain\water\density\shwa15.shp',
    r'E:\work\sv_goufu\datatrain\water\density\shwa19.shp',
    r'E:\work\sv_goufu\datatrain\water\density\shwa22.shp',
]
# for file_path in shp_file_paths:
#     water_density_temper_shp_file = gpd.read_file(file_path)
#     print(f"Processing file: {file_path}")

#     filtered_data = temper_shp_file[temper_shp_file ['densitywa'] > -9999]
#     print(filtered_data.shape)
#     print(filtered_data.crs)

shp_file_paths=[
    r'E:\work\sv_goufu\datatrain\water\length\点数据源\sh00.shp',
    r'E:\work\sv_goufu\datatrain\water\length\点数据源\sh05.shp',
    r'E:\work\sv_goufu\datatrain\water\length\点数据源\sh10.shp',
    r'E:\work\sv_goufu\datatrain\water\length\点数据源\sh15.shp',
    r'E:\work\sv_goufu\datatrain\water\length\点数据源\sh19.shp',
    r'E:\work\sv_goufu\datatrain\water\length\点数据源\sh22.shp',
]
# for file_path in shp_file_paths:
#     water_length_temper_shp_file = gpd.read_file(file_path)
#     print(f"Processing file: {file_path}")

#     filtered_data = water_length_temper_shp_file[water_length_temper_shp_file ['RASTERVALU'] > -9999]
#     print(filtered_data.shape)
#     print(filtered_data.crs)

# 使用uid字段合并所有相关数据
# densitywat