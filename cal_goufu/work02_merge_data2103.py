import geopandas as gpd
from tqdm import tqdm  # 用于显示进度条

def merge_shp_data(year):
    # 主文件路径
    main_file = f'e:\\work\\sv_goufu\\datatrain\\bird02\\tongji\\tj21.shp'
    # main_file = r'e:\work\sv_goufu\datatrain\dem\点数据\dem.shp'
    
    # 数据源字典 {文件路径: 需要提取的列名}
    data_sources ={
        '00': {
        r'e:\work\sv_goufu\datatrain\dem\点数据\dem.shp': 'dem',
        r'E:\work\sv_goufu\datatrain\lightyear\点数据\ylight00.shp': 'ylight',
        r'E:\work\sv_goufu\datatrain\ndvi\点数据\00nd点.shp': 'ndvi',
        r'e:\work\sv_goufu\datatrain\podu\点数据\shpod.shp': 'podu',
        r'E:\work\sv_goufu\datatrain\population\点数据\00shpop.shp': 'population',
        r'E:\work\sv_goufu\datatrain\road2\点数据\road15.shp': 'road2',
        r'E:\work\sv_goufu\datatrain\water\length\点数据源\sh00.shp': 'lengthwa',
        },  
        '05': {
        r'e:\work\sv_goufu\datatrain\dem\点数据\dem.shp': 'dem',
        r'E:\work\sv_goufu\datatrain\lightyear\点数据\ylight05.shp': 'ylight',
        r'E:\work\sv_goufu\datatrain\ndvi\点数据\05nd点.shp': 'ndvi',
        r'e:\work\sv_goufu\datatrain\podu\点数据\shpod.shp': 'podu',
        r'E:\work\sv_goufu\datatrain\population\点数据\05shpop.shp': 'population',
        r'E:\work\sv_goufu\datatrain\road2\点数据\road15.shp': 'road2',
        r'E:\work\sv_goufu\datatrain\water\length\点数据源\sh05.shp': 'lengthwa',
        },  
        '10': {
        r'e:\work\sv_goufu\datatrain\dem\点数据\dem.shp': 'dem',
        r'E:\work\sv_goufu\datatrain\lightyear\点数据\ylight10.shp': 'ylight',
        r'E:\work\sv_goufu\datatrain\ndvi\点数据\10nd点.shp': 'ndvi',
        r'e:\work\sv_goufu\datatrain\podu\点数据\shpod.shp': 'podu',
        r'E:\work\sv_goufu\datatrain\population\点数据\10shpop.shp': 'population',
        r'E:\work\sv_goufu\datatrain\road2\点数据\road15.shp': 'road2',
        r'E:\work\sv_goufu\datatrain\water\length\点数据源\sh10.shp': 'lengthwa',
        },  
        '15': {
        r'e:\work\sv_goufu\datatrain\dem\点数据\dem.shp': 'dem',
        r'E:\work\sv_goufu\datatrain\lightyear\点数据\ylight15.shp': 'ylight',
        r'E:\work\sv_goufu\datatrain\ndvi\点数据\15nd点.shp': 'ndvi',
        r'e:\work\sv_goufu\datatrain\podu\点数据\shpod.shp': 'podu',
        r'E:\work\sv_goufu\datatrain\population\点数据\15shpop.shp': 'population',
        r'E:\work\sv_goufu\datatrain\road2\点数据\road15.shp': 'road2',
        r'E:\work\sv_goufu\datatrain\water\length\点数据源\sh15.shp': 'lengthwa',
        },  
        '20': {
        r'e:\work\sv_goufu\datatrain\dem\点数据\dem.shp': 'dem',
        r'E:\work\sv_goufu\datatrain\lightyear\点数据\ylight20.shp': 'ylight',
        r'E:\work\sv_goufu\datatrain\ndvi\点数据\20nd点.shp': 'ndvi',
        r'e:\work\sv_goufu\datatrain\podu\点数据\shpod.shp': 'podu',
        r'E:\work\sv_goufu\datatrain\population\点数据\20shpop.shp': 'population',
        r'E:\work\sv_goufu\datatrain\road2\点数据\road20.shp': 'road2',
        r'E:\work\sv_goufu\datatrain\water\length\点数据源\sh19.shp': 'lengthwa',
        },  
        '24': {
        r'e:\work\sv_goufu\datatrain\dem\点数据\dem.shp': 'dem',
        r'E:\work\sv_goufu\datatrain\lightyear\点数据\ylight23.shp': 'ylight',
        r'E:\work\sv_goufu\datatrain\ndvi\点数据\24nd点.shp': 'ndvi',
        r'e:\work\sv_goufu\datatrain\podu\点数据\shpod.shp': 'podu',
        r'E:\work\sv_goufu\datatrain\population\点数据\23shpop.shp': 'population',
        r'E:\work\sv_goufu\datatrain\road2\点数据\road25.shp': 'road2',
        r'E:\work\sv_goufu\datatrain\water\length\点数据源\sh22.shp': 'lengthwa',
        },  
    }
    
# 筛选相关性
# dem
# ylight
# ndvi
# podu ---
# population ---
# road2
# lengthwa

    try:
        # 1. 读取主文件并提取所需列
        print("正在读取主文件...")
        main_gdf = gpd.read_file(main_file)

        # 检查必需列是否存在
        if 'uid' not in main_gdf.columns or 'Join_Count' not in main_gdf.columns:
            missing_cols = [col for col in ['uid', 'Join_Count'] if col not in main_gdf.columns]
            raise ValueError(f"主文件中缺少必要列: {missing_cols}")
        
        # 创建结果GeoDataFrame，只保留几何、uid和Join_Count列
        result_gdf = main_gdf[['uid', 'Join_Count', 'geometry']].copy()
        
        # 2. 循环处理每个数据源文件
        print("开始合并数据源...")
        for src_file, column_name in tqdm(data_sources[year].items(), desc="处理进度"):
            try:
                # 读取数据源文件
                src_gdf = gpd.read_file(src_file)
                
                # 检查所需列是否存在
                if column_name not in src_gdf.columns:
                    print(f"警告: 文件 {src_file} 中不存在列 {column_name}，已跳过")
                    continue
                
                # 检查uid列是否存在
                if 'uid' not in src_gdf.columns:
                    print(f"警告: 文件 {src_file} 中不存在uid列，无法合并，已跳过")
                    continue
                
                # 提取所需列并合并到结果中
                temp_df = src_gdf[['uid', column_name]]
                        
                result_gdf = result_gdf.merge(temp_df, on='uid', how='left')
                
                # print(temp_df.shape)
                print(result_gdf.shape)
                # raise ValueError("测试异常")  # 测试异常处理
                
            except Exception as e:
                print(f"处理文件 {src_file} 时出错: {str(e)}")
                continue
        
        # 3. 保存结果
        print("正在保存合并后的文件...")

        # 输出文件路径
        output_file = f'E:\\work\\sv_goufu\\MLP2025042801\\year{year}.shp'
        result_gdf.to_file(output_file)
        print(f"合并完成！结果已保存到: {output_file}")
        
        # 打印合并后的列名
        print("\n合并后的列名:")
        print(result_gdf.columns.tolist())
        
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")

if __name__ == "__main__":
    # merge_shp_data()

    # years = ['98','99','00',
    # '01','02','03','04','05','06','07','08','09','10',
    # '11','12','13','14','15','16','17','18','19','20',
    # '21','22','23',]
    years = ['00','05','10','15','20','24']

    for year in years:
        print(year)
        merge_shp_data(year)



