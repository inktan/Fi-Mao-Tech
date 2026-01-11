import csv
import time
from tqdm import tqdm
import requests
import re
import pandas as pd
from datetime import datetime
from requests.models import Response
import geopandas as gpd

def make_search_url(lat: float, lon: float) -> str:
    """
    Builds the URL of the script on Google's servers that returns the closest
    panoramas (ids) to a give GPS coordinate.
    """
    url = (
        "https://maps.googleapis.com/maps/api/js/"
        "GeoPhotoService.SingleImageSearch"
        "?pb=!1m5!1sapiv3!5sUS!11m2!1m1!1b0!2m4!1m2!3d{0:}!4d{1:}!2d50!3m10"
        "!2m2!1sen!2sGB!9m1!1e2!11m4!1m3!1e2!2b1!3e2!4m10!1e1!1e2!1e3!1e4"
        "!1e8!1e6!5m1!1e2!6m1!1e2"
        "&callback=_xdc_._v2mub5"
    )
    return url.format(lat, lon)

def search_request(lat: float, lon: float) -> Response:
    """
    Gets the response of the script on Google's servers that returns the
    closest panoramas (ids) to a give GPS coordinate.
    """
    url = make_search_url(lat, lon)
    while True:
        try:
            response = requests.get(url, timeout=10)
            break
        except (requests.ConnectionError, requests.Timeout):
            print("Connection error or timeout. Trying again in 2 seconds.")
            time.sleep(2)
    return response

def panoids_from_response(text, closest=False, disp=False, proxies=None):
    """
    Gets panoids from response (gotting asynchronously)
    """
    pans = re.findall('\[[0-9]+,"(.+?)"\].+?\[\[null,null,(-?[0-9]+\.[0-9]+),(-?[0-9]+\.[0-9]+).*?\],\s*\[(-?[0-9]+\.[0-9]+).*?\[(-?[0-9]+\.[0-9]+),(-?[0-9]+\.[0-9]+),(-?[0-9]+\.[0-9]+)\]', text)
    pans = [{
        "panoid": p[0],
        "lat": float(p[1]),
        "lon": float(p[2]),
        "pitch": float(p[3]),
        "heading": float(p[4]),
        "fov01": float(p[5]),
        "fov02": float(p[6]),
        } for p in pans]  # Convert to floats

    pans = [p for i, p in enumerate(pans) if p not in pans[:i]]

    if disp:
        for pan in pans:
            print(pan)

    dates = re.findall('([0-9]?[0-9]?[0-9])?,?\[(20[0-9][0-9]),([0-9]+)\]', text)
    dates = [list(d)[1:] for d in dates]  # Convert to lists and drop the index

    if len(dates) > 0:
        dates = [[int(v) for v in d] for d in dates]
        dates = [d for d in dates if d[1] <= 12 and d[1] >= 1]
        year, month = dates.pop(-1)
        pans[0].update({'year': year, "month": month})
        dates.reverse()
        for i, (year, month) in enumerate(dates):
            pans[-1-i].update({'year': year, "month": month})

    def func(x):
        if 'year' in x:
            return (-x['year'], -x['month'])
        else:
            return (float('inf'), float('inf'))

    pans.sort(key=func)

    if closest:
        return [pans[i] for i in range(len(dates))]
    else:
        return pans

def main(csv_path, sv_infos_path, start_index=None, end_index=None):
    df = pd.read_csv(csv_path)
    
    # 筛选指定index范围的数据
    if start_index is not None and end_index is not None:
        df = df[(df.index >= start_index) & (df.index <= end_index)]
        print(f"Processing rows from index {start_index} to {end_index}")
    elif start_index is not None:
        df = df[df.index >= start_index]
        print(f"Processing rows from index {start_index} to end")
    elif end_index is not None:
        df = df[df.index <= end_index]
        print(f"Processing rows from start to index {end_index}")
    
    print(f"Total rows to process: {df.shape[0]}")

    # Initialize buffer and counter
    buffer = []
    count = 0
    save_interval = 1000

    # Create CSV file with headers if it doesn't exist
    with open(sv_infos_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ORIG_FID','rid','longitude','latitude','panoid','pitch','heading','fov01','fov02','year','month'])

    for index, row in tqdm(df.iterrows(), total=df.shape[0]):
        # 使用原始的index（从CSV中读取的），而不是重置后的index
        original_index = index
        
        try:
            # resp = search_request(float(row['latitude']), float(row['longitude']))
            resp = search_request(float(row['latY']), float(row['lngX']))
            panoids = panoids_from_response(resp.text)
        except Exception as e:
            print(f"Error processing row {original_index}: {e}")
            continue

        if len(panoids) == 0:
            continue

        for pano in panoids:
            try:
                year = int(pano.get('year', 0))
                month = int(pano.get('month', 0))
            except Exception as e:
                year = 0
                month = 0

            # if year < 2022:
            #     continue

            # Add record to buffer
            buffer.append([
                original_index,  # 使用原始的index
                int(row['ORIG_FID']),
                int(row['rid']),
                float(row['lngX']),
                float(row['latY']),
                pano['panoid'],
                pano['pitch'],
                pano['heading'],
                pano['fov01'],
                pano['fov02'],
                year,
                month
            ])

            count += 1

            # Save to CSV every 1000 records
            if len(buffer) >= save_interval:
                with open(sv_infos_path, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerows(buffer)
                print(f"Saved {len(buffer)} records to CSV (total: {count})")
                buffer = []  # Clear buffer

    # Save any remaining records in buffer
    if len(buffer) > 0:
        with open(sv_infos_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(buffer)
        print(f"Saved final {len(buffer)} records to CSV (total: {count})")

if __name__ == "__main__":
    start_index = 0
    end_index = 20000

    csv_path = r'e:\work\sv_pangpang\4_tree_species_deeplearning\GIS_data\CoS_GSV_30m_points.shp' # 需要爬取的点
    sv_infos_path = r'e:\work\sv_pangpang\4_tree_species_deeplearning\GIS_data\CoS_GSV_30m_points_infos.csv' # 爬取结果保存路径

    main(csv_path, sv_infos_path, start_index, end_index)
