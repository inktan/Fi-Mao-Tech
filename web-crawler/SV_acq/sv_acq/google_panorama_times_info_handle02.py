# -*- coding: utf-8 -*-
import csv
import time
from tqdm import tqdm
import os
import numpy as np
import json
import pandas as pd
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
    """
    Gets panoids from response (gotting asynchronously)
    """

    # Get all the panorama ids and coordinates
    # I think the latest panorama should be the first one. And the previous
    # successive ones ought to be in reverse order from bottom to top. The final
    # images don't seem to correspond to a particular year. So if there is one
    # image per year I expect them to be orded like:
    # 2015
    # XXXX
    # XXXX
    # 2012
    # 2013
    # 2014
    pans = re.findall('\[[0-9]+,"(.+?)"\].+?\[\[null,null,(-?[0-9]+.[0-9]+),(-?[0-9]+.[0-9]+)', text)
    pans = [{
        "panoid": p[0],
        "lat": float(p[1]),
        "lon": float(p[2])} for p in pans]  # Convert to floats

    # Remove duplicate panoramas
    pans = [p for i, p in enumerate(pans) if p not in pans[:i]]

    if disp:
        for pan in pans:
            print(pan)

    # Get all the dates
    # The dates seem to be at the end of the file. They have a strange format but
    # are in the same order as the panoids except that the latest date is last
    # instead of first.
    dates = re.findall('([0-9]?[0-9]?[0-9])?,?\[(20[0-9][0-9]),([0-9]+)\]', text)
    dates = [list(d)[1:] for d in dates]  # Convert to lists and drop the index

    if len(dates) > 0:
        # Convert all values to integers
        dates = [[int(v) for v in d] for d in dates]

        # Make sure the month value is between 1-12
        dates = [d for d in dates if d[1] <= 12 and d[1] >= 1]

        # The last date belongs to the first panorama
        year, month = dates.pop(-1)
        pans[0].update({'year': year, "month": month})

        # The dates then apply in reverse order to the bottom panoramas
        dates.reverse()
        for i, (year, month) in enumerate(dates):
            pans[-1-i].update({'year': year, "month": month})

    # # Make the first value of the dates the index
    # if len(dates) > 0 and dates[-1][0] == '':
    #     dates[-1][0] = '0'
    # dates = [[int(v) for v in d] for d in dates]  # Convert all values to integers
    #
    # # Merge the dates into the panorama dictionaries
    # for i, year, month in dates:
    #     pans[i].update({'year': year, "month": month})

    # Sort the pans array
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

def GSVpanoMetadataCollector():
    
    # 读取CSV文件，并保存'lat'和'lon'同时不重复的列数据
    # df_unique = pd.read_csv(input_csv).drop_duplicates(subset=['long', 'lat'])
    # print(df_unique.shape)
    # csv_file = r'e:\work\sv_j_ran\sv_google_20240903\data_coor_unique.csv'
    # df_unique.to_csv(csv_file, index=False)
    
    json_dict={}
    with open(input_csv, 'r') as f:  
        reader = csv.reader(f)
        mylist = list(reader)
        count = 0
        # print(mylist)
        for row in tqdm(mylist):
            count += 1
            if count == 1 or len(row)<3:
                continue
            # if count > 55000:
            #     continue
            # if count > 100 :
            #     continue
            
            id = row[0]
            lon = row[2]
            lat = row[1]
        
            panos = []
            try:
                
                resp = search_request(lat, lon)
                panoids = panoids_from_response(resp.text)
                
            except Exception as e :
                print(f'error:{e}')
                continue

            panoramas_info = []
            for pano in panos:
                pand_info={}
                if pano.date is not None:
                    data = pano.date.split('-')
                    
                    pand_info['pano_id']=pano.pano_id
                    pand_info['heading']=pano.heading
                    pand_info['pitch']=pano.pitch
                    pand_info['date_year_month']=data[0]+'_'+data[1]
                    pand_info['year_month']=int(data[0])+int(data[1])/12.0
                    pand_info['year']=int(data[0])
                    pand_info['month']=int(data[1])/12
                    
                    panoramas_info.append(pand_info)
                else:
                    # 使用列表推导式和 any() 函数来判断列表中是否包含特定的键值对
                    key_to_check = 'date_year_month'
                    value_to_check = ''
                    contains_key_value_pair = any(d[key_to_check] == value_to_check for d in panoramas_info if key_to_check in d)

                    if not contains_key_value_pair:
                        pand_info['pano_id']=pano.pano_id
                        pand_info['heading']=pano.heading
                        pand_info['pitch']=pano.pitch
                        pand_info['date_year_month']=''
                        pand_info['year_month']=0
                        pand_info['year']=0
                        pand_info['month']=0
                            
                        panoramas_info.append(pand_info)
            json_dict[id] = panoramas_info
            
            if count%1000==0:
                with open(json_file_path, 'w', encoding='utf-8') as file:
                    json.dump(json_dict, file, ensure_ascii=False, indent=4)

    with open(json_file_path, 'w', encoding='utf-8') as file:
        json.dump(json_dict, file, ensure_ascii=False, indent=4)
        
if __name__ == "__main__":
    # 输入经纬度点的csv文件
    input_csv = r'e:\work\sv_yantu\points.csv'
    # 输入街景保存文件夹
    json_file_path = r'e:\work\sv_yantu\data_coor_id_panoramas_infos.json'
    
    GSVpanoMetadataCollector()
