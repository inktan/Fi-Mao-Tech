import pandas as pd

csv_path =  r'd:\work\sv_yj\sv_phoenix\merged_data.csv'
df = pd.read_csv(csv_path)

# 假设 df 是你的 DataFrame
df['img_id'] = df['doitt_id'].astype(int).astype(str) + '_' + df['categories'].astype(int).astype(str)

output_file_path = r'd:\work\sv_yj\sv_phoenix\merged_data_id.csv'
df.to_csv(output_file_path, index=False)

print(f"合并后的文件已保存到 {output_file_path}")


