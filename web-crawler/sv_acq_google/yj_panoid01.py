import os
import pandas as pd
from streetview import search_panoramas
from tqdm import tqdm

input_file_path = 'e:\work\sv_YJ\sv_20250901\Phoenix.csv'
df = pd.read_csv(input_file_path)

pano_data = []

for index, row in tqdm(df.iterrows(), total=len(df)):
    input_lat = row['lon']
    input_lon = row['lat']
    building_id = row['doitt_id']
    fov_1_ori = row['fov1']
    fov_2_ori = row['fov2']
    pitch_ori = row['pitch']
    categories = row['categories']
    heading_ori = row['heading']

    try:
        panos = search_panoramas(lat=input_lat, lon=input_lon)
        
        valid_panos = []
        
        for pano in panos:
            if not pano.date or '-' not in pano.date:
                continue
            
            date_parts = pano.date.split('-')
            year = date_parts[0]
            month = date_parts[1] if len(date_parts) > 1 else ''
            
            if year.isdigit() and month.isdigit():
                valid_panos.append({
                    "input_lat": input_lat,
                    "input_lon": input_lon,
                    "building_id_ori": building_id,
                    "categories_ori": categories,
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
                    "year": int(year),
                    "month": int(month),
                    "date_str": pano.date
                })
        
        if valid_panos:
            valid_panos.sort(key=lambda x: (x['year'], x['month']), reverse=True)
            latest_pano = valid_panos[0]
            pano_data.append(latest_pano)
            
    except Exception as e:
        print(f"处理纬度{input_lat}和经度{input_lon}时发生异常：{e}")

result_df = pd.DataFrame(pano_data)

print(f"总共处理了 {len(pano_data)} 个最新的街景数据点")
result_df.to_csv('e:\\work\\sv_YJ\\sv_20250901\\Phoenix_latest_panos.csv', index=False)