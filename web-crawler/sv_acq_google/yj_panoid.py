
import os
import pandas as pd
from streetview import search_panoramas
from tqdm import tqdm

# 读取CSV文件
input_file_path = 'e:\work\sv_YJ\sv_20250901\Phoenix.csv'

# ZR：改成stand point csv的位置------------------------------------------------
# 使用pandas读取CSV文件
df = pd.read_csv(input_file_path)
df

# 读取CSV文件
hdbs = df

# 初始化一个空列表来收集数据
pano_data = []

# 遍历每一行数据
for index, row in tqdm(hdbs.iterrows(),total=len(hdbs)):
    input_lat = row['lon']
    input_lon = row['lat']
    building_id = row['doitt_id']
    fov_1_ori = row['fov1']
    fov_2_ori = row['fov2']
    pitch_ori = row['pitch']
    categories = row['categories']
    heading_ori = row['heading']

    # print(f"正在处理第{index + 1}行：纬度{input_lat}, 经度{input_lon}")

    try:
        # 尝试获取街景图像数据
        panos = search_panoramas(lat=input_lat, lon=input_lon)
        # print(f"找到{len(panos)}个街景图像")
        for pano in panos:
            # print(f"处理pano_id:{pano.pano_id}")
            if not pano.date or '-' not in pano.date:
                # print(f"跳过pano_id:{pano.pano_id}，因为日期格式不正确：{pano.date}")
                continue
            date_parts = pano.date.split('-')
            year = date_parts[0]
            month = date_parts[1] if len(date_parts) > 1 else ''
            pano_data.append({
                "input_lat": input_lat,
                "input_lon": input_lon,
                "building_id_ori": building_id,
                "categories_ori" : categories,
                "heading_ori": heading_ori,
                "fov1_ori": fov_1_ori,
                "fov2_ori": fov_2_ori,
                "pitch_ori": pitch_ori,
                "pano_id": pano.pano_id,
                "lat": pano.lat,
                "lon": pano.lon,
                "heading": pano.heading,
                "pitch": pano.pitch,
                "roll": pano.roll,
                "year": year,
                "month": month
            })
    except Exception as e:
        print(f"处理纬度{input_lat}和经度{input_lon}时发生异常：{e}")

# 将列表转换为DataFrame
pano_df = pd.DataFrame(pano_data)

# 保存DataFrame到CSV文件
output_path = 'e:\work\sv_YJ\sv_20250901\Phoenix_panoid.csv'
pano_df.to_csv(output_path, index=False)

if not pano_data:
    print("没有收集到任何街景图像数据，输出文件将为空。")
else:
    print(f"文件已保存到{output_path}")

# 只要最新年份的

import pandas as pd
# 选择每个点最新年份的记录
latest_year_df = pano_df.loc[pano_df.groupby('input_lon')['year'].idxmax()]

# 保存新的 DataFrame 到 CSV 文件
latest_year_df.to_csv('e:\work\sv_YJ\sv_20250901\Phoenix_panoid_only_latest_year.csv', index=False)  #ZR： 改要保存在哪里-------------------------------------------------------------

# 分成n份用于分布式下载

# 想要分成多少份
n = 4

# 输出目录
output_dir = "e:\work\sv_YJ\sv_20250901\Phoenix_splits" #修改文件夹名字
os.makedirs(output_dir, exist_ok=True)

# 每份的大小
import math
chunk_size = math.ceil(len(latest_year_df) / n)

for i in range(n):
    start_idx = i * chunk_size
    end_idx = start_idx + chunk_size
    chunk_df = latest_year_df.iloc[start_idx:end_idx]

    output_path = os.path.join(output_dir, f"boston_panoid_latest_year_part{i+1}.csv")
    chunk_df.to_csv(output_path, index=False)
    print(f"保存完成: {output_path}, 共 {len(chunk_df)} 行")


