import pandas as pd

# 读取两个CSV文件
pd01 = pd.read_csv(r'd:\work\sv_yj\0920\0530_5_NY_standpoint_final_with_image_id.csv')  # 替换为你的第二个文件路径
pd02 = pd.read_csv(r'd:\work\sv_yj\0920\image_file_info_01.csv')  # 替换为你的第一个文件路径

# 创建一个新的DataFrame来存储结果
result_df = pd.DataFrame()

# 遍历pd01的每一行
for index, row in pd01.iterrows():
    # 获取当前行的panoid值
    panoid_value = row['image_id']
    
    # 在pd02中查找匹配的行
    matched_rows = pd02[pd02['image_id'] == panoid_value]
    
    # 如果存在匹配行
    if not matched_rows.empty:
        # 获取第一个匹配行
        matched_row = matched_rows.iloc[0]
        
        # 创建当前行的副本
        new_row = row.copy()
        
        # 添加pd02中其他列的数据（除了panoid列）
        for col in pd02.columns:
            if col != 'image_id':
                new_row[col] = matched_row[col]
        
        # 将新行添加到结果DataFrame中
        result_df = pd.concat([result_df, new_row.to_frame().T], ignore_index=True)

# 重置索引
result_df.reset_index(drop=True, inplace=True)

# 显示结果
print(result_df)

# 如果需要保存到新的CSV文件
result_df.to_csv(r'd:\work\sv_yj\0920\image_file_info_021.csv', index=False)


