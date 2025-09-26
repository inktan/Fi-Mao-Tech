import pandas as pd

# 读取两个CSV文件
pd01 = pd.read_csv(r'd:\work\sv_yj\0920\0530_5_NY_standpoint_final_with_image_id.csv')  # 替换为你的第二个文件路径
pd02 = pd.read_csv(r'd:\work\sv_yj\0920\image_file_info_02.csv')  # 替换为你的第一个文件路径

result_df = pd.merge(pd01, pd02, on='image_id', how='left')

print(result_df)
print(result_df.columns)

result_df.to_csv(r'd:\work\sv_yj\0920\0530_5_NY_standpoint_final_with_image_id_02.csv', index=False)



