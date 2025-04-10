import geopandas as gpd
from tqdm import tqdm  # 用于显示进度条

def merge_shp_data():
    # 主文件路径
    main_file = r'e:\work\sv_goufu\datatrain\bird02\tongji\tj21.shp'
    
    # 数据源字典 {文件路径: 需要提取的列名}
    data_sources = {
        r'e:\work\sv_goufu\datatrain\coastline\点数据\shcoastline.shp': 'NEAR_DIST',
        r'e:\work\sv_goufu\datatrain\dem\点数据\dem.shp': 'dem',
        r'E:\work\sv_goufu\datatrain\green\fishnet\shgren22.shp': 'density',
        r'E:\work\sv_goufu\datatrain\landcoverpre\点数据\sh22.shp': 'landcover',
        r'E:\work\sv_goufu\datatrain\lightyear\点数据\ylight20.shp': 'ylight',
        r'E:\work\sv_goufu\datatrain\ndvi\点数据\20nd点.shp': 'ndvi',
        r'e:\work\sv_goufu\datatrain\podu\点数据\shpod.shp': 'podu',
        r'E:\work\sv_goufu\datatrain\population\点数据\20shpop.shp': 'population',
        r'e:\work\sv_goufu\datatrain\poxiang\点数据\shpoxiang.shp': 'poxiang',
        r'E:\work\sv_goufu\datatrain\rain\点数据\20.shp': 'rain',
        r'E:\work\sv_goufu\datatrain\road2\点数据\road20.shp': 'road2',
        r'e:\work\sv_goufu\datatrain\temper\点数据\20.shp': 'temper',
        r'E:\work\sv_goufu\datatrain\water\density\shwa22.shp': 'densitywa',
        r'E:\work\sv_goufu\datatrain\water\length\点数据源\sh22.shp': 'lengthwa',
    }
    
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
        for src_file, column_name in tqdm(data_sources.items(), desc="处理进度"):
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
        output_file = r'E:\work\sv_goufu\MLP\year21\MLP21.shp'
        result_gdf.to_file(output_file)
        print(f"合并完成！结果已保存到: {output_file}")
        
        # 打印合并后的列名
        print("\n合并后的列名:")
        print(result_gdf.columns.tolist())
        
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")

if __name__ == "__main__":
    merge_shp_data()


# # 因变量-鸟
# \datatrain\bird02\tongji\tj21.shp'

# # 自变量-环境因子
# \coastline\点数据\shcoastline.shp': 'NEAR_DIST',
# \dem\点数据\dem.shp': 'dem',
# \green\fishnet\shgren22.shp': 'density',
# \landcoverpre\点数据\sh22.shp': 'landcover',
# \lightyear\点数据\ylight20.shp': 'ylight',
# \ndvi\点数据\20nd点.shp': 'ndvi',
# \podu\点数据\shpod.shp': 'podu',
# \population\点数据\20shpop.shp': 'population',
# \poxiang\点数据\shpoxiang.shp': 'poxiang',
# \rain\点数据\20.shp': 'rain',
# \road2\点数据\road20.shp': 'road2',
# \temper\点数据\20.shp': 'temper',
# \water\density\shwa22.shp': 'densitywa',
# \water\length\点数据源\sh22.shp': 'lengthwa',
