import pandas as pd

try:
    # 读取CSV文件
    df = pd.read_csv(r'd:\work\sv_taiwan\sv_pan_names03.csv')
    
    # 分割ID列
    split_data = df['index'].str.split('_', expand=True)
    
    # 检查是否成功分割出足够列
    if split_data.shape[1] < 4:
        raise ValueError("ID列格式不符合预期，无法提取经纬度信息")
    
    # 提取并转换经纬度为数值类型
        
    combined_df = pd.DataFrame()
        
    combined_df['osm_id'] = pd.to_numeric(split_data[1], errors='coerce')
    combined_df['longitude'] = pd.to_numeric(split_data[2], errors='coerce')
    combined_df['latitude'] = pd.to_numeric(split_data[3], errors='coerce')
    
    # 检查是否有无效的经纬度
    # if df[['lon', 'lat']].isnull().any().any():
    #     print("警告：部分经纬度数据无效，将被设为NaN")
    
    # 删除原始列
    # df = df.drop(columns=['id'])
    
    # 保存结果
    combined_df.to_csv(r'd:\work\sv_taiwan\sv_pan_names03_points.csv', index=False)

except Exception as e:
    print(f"处理过程中发生错误: {str(e)}")