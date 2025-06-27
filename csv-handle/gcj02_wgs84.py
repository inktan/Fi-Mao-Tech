import pandas as pd
from coord_convert.transform import gcj2wgs  # 确保已安装coord_convert库

# 读取原始CSV文件
input_file = r'e:\work\sv_zoudaobuhuang\points\points_test.csv'  # 替换为你的输入文件名
output_file = r'e:\work\sv_zoudaobuhuang\points\points_wgs84.csv'  # 输出文件名

# 读取数据
df = pd.read_csv(input_file)

# 检查列是否存在
if 'lon' not in df.columns or 'lat' not in df.columns:
    raise ValueError("CSV文件中必须包含'lon'和'lat'列")

# 转换坐标系
df['lon'], df['lat'] = zip(*df.apply(
    lambda row: gcj2wgs(row['lon'], row['lat']), axis=1
))

# 保存结果到新CSV文件
df.to_csv(output_file, index=False)

print(f"转换完成，结果已保存到 {output_file}")

