import csv
import time
from tqdm import tqdm
import os
import numpy as np
import itertools
import time
from dataclasses import dataclass
from io import BytesIO
from typing import Generator, Tuple
import requests
from PIL import Image
import json
import re
from typing import List, Optional
import requests
from pydantic import BaseModel
from requests.models import Response
import time
from datetime import datetime
import pandas as pd  

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
        "&callback=callbackfunc"
    )
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
            response = requests.get(url)
            break
        except requests.ConnectionError:
            print("Connection error. Trying again in 2 seconds.")
            time.sleep(2)

    return response

def panoids_from_response(text, closest=False, disp=False, proxies=None):
    pans = re.findall('\[[0-9]+,"(.+?)"\].+?\[\[null,null,(-?[0-9]+.[0-9]+),(-?[0-9]+.[0-9]+)', text)
    pans = [{
        "panoid": p[0],
        "lat": float(p[1]),
        "lon": float(p[2])} for p in pans]  # Convert to floats

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
        if 'year'in x:
            return datetime(year=x['year'], month=x['month'], day=1)
        else:
            return datetime(year=3000, month=1, day=1)
    pans.sort(key=func)

    if closest:
        return [pans[i] for i in range(len(dates))]
    else:
        return pans
def main(csv_path,sv_infos_path):
    # 创建一个空列表来存储行数据
    rows = []
    df = pd.read_csv(csv_path)
    print(df.shape)

    # 遍历每一行数据
    count=0
    for index, row in tqdm(df.iterrows()):
        # if index <= 6612:
        #     continue
        # if index >16000:
        #     continue

        print(index,float(row['longitude']),float(row['latitude']))
        print(df.shape)

        try:
            resp = search_request(float(row['latitude']), float(row['longitude']))
            panoids = panoids_from_response(resp.text)
        except Exception as e:
            print(e)
            continue
        if len(panoids)==0:
            continue
        pano = panoids[0]
        try :
            year = int(pano['year'])
            month = int(pano['month'])
        except Exception as e :
            year = 0
            month = 0
            # print(pano)
            # print(year)
            # print(month)

        with open(sv_infos_path,'a' ,newline='') as f:
            writer = csv.writer(f)
            writer.writerow([count,float(row['longitude']),float(row['latitude']),pano['panoid'], year, month])
            print(count)
            count+=1

csv_path = r'/content/gdrive/MyDrive/sv_points/merged_coordinates_01.csv' # 需要爬取的点
sv_infos_path = csv_path.replace('.csv','_sv_infos_.csv')

with open(sv_infos_path,'w' ,newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['id','longitude','latitude','panoid','year','month'])

start_inedx = 0
end_index = 2495000000

main(csv_path,sv_infos_path)
