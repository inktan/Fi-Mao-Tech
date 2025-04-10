import geopandas as gpd

shp_file_paths=[
    r'E:\work\sv_goufu\datatrain\water\length\点数据源\sh00.shp',
    r'E:\work\sv_goufu\datatrain\water\length\点数据源\sh05.shp',
    r'E:\work\sv_goufu\datatrain\water\length\点数据源\sh10.shp',
    r'E:\work\sv_goufu\datatrain\water\length\点数据源\sh15.shp',
    r'E:\work\sv_goufu\datatrain\water\length\点数据源\sh19.shp',
    r'E:\work\sv_goufu\datatrain\water\length\点数据源\sh22.shp',
]

for file_path in shp_file_paths:
    gdf = gpd.read_file(file_path)
    print(f"Processing file: {file_path}")
    print(gdf.columns)  # 打印所有列名
    # if 'RASTERVALU' in gdf.columns:
    #     # 重命名列
    #     gdf = gdf.rename(columns={'RASTERVALU': 'lengthwa'})
    #     gdf.to_file(file_path)  # 保存修改后的文件