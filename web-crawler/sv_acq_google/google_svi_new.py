import csv
from tqdm import tqdm
import re
from requests.models import Response
import time
import pandas as pd
from PIL import Image
from dataclasses import dataclass
from typing import Generator, Tuple
from datetime import datetime
import itertools
from io import BytesIO
import requests
import os

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
    # print("Parsing response...")
    # print('length of text:',len(text))
    # print(text[0:200])
    
    first_part = text[:3000]
    last_part = text[-30000:] if len(text) > 30000 else text
    text = first_part + last_part
    
    pans = re.findall('\[[0-9]+,"(.+?)"\].+?\[\[null,null,(-?[0-9]+\.[0-9]+),(-?[0-9]+\.[0-9]+).*?\],\s*\[(-?[0-9]+\.[0-9]+).*?\[(-?[0-9]+\.[0-9]+),(-?[0-9]+\.[0-9]+),(-?[0-9]+\.[0-9]+)\]', text)
    # pans = re.findall('\[[0-9]+,"(.+?)"\].+?\[\[null,null,(-?[0-9]+.[0-9]+),(-?[0-9]+.[0-9]+)', text)
    # print('length of pans:',len(pans))
    pans = [{
        "panoid": p[0],
        "lat": float(p[1]),
        "lon": float(p[2]),
        "pitch": float(p[3]),
        "heading": float(p[4]),
        "fov01": float(p[5]),
        "fov02": float(p[6]),
        } for p in pans]  # Convert to floats

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
        if 'year' in x:
            # 返回一个元组，year 取负值（实现降序），month 取负值（实现降序）
            return (-x['year'], -x['month'])
        else:
            # 没有 'year' 键的元素排在最后
            return (float('inf'), float('inf'))

    pans.sort(key=func)

    if closest:
        return [pans[i] for i in range(len(dates))]
    else:
        return pans

def get_streetview(panoid, width, height, pitch, yaw):
    """
    获取 Google 街景缩略图并返回 Pillow Image 对象
    
    参数:
        panoid (str): 街景全景ID
        width (int): 图像宽度，默认1100
        height (int): 图像高度，默认600
        pitch (int): 俯仰角度，默认0
        yaw (int): 偏航角度，默认90
    
    返回:
        PIL.Image.Image: Pillow 图像对象
    """
    # 构建请求URL
    url = f"https://streetviewpixels-pa.googleapis.com/v1/thumbnail?cb_client=maps_sv.tactile&w={width}&h={height}&pitch={pitch}&panoid={panoid}&yaw={yaw}"
    
    try:
        # 发送GET请求
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 检查请求是否成功
        
        # 将响应内容转换为Pillow Image对象
        image = Image.open(BytesIO(response.content))
        
        return image
    
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return None
    except Exception as e:
        print(f"处理图像时出错: {e}")
        return None

def main(csv_path,output_):
    df = pd.read_csv(csv_path)
    print(df.shape)
    for index, row in tqdm(df.iterrows()):
        if index <= 385:
            continue
        # if index >750000000:
        #     continue
        print(df.shape[0],index)
        try:
            resp = search_request(float(row['latitude']), float(row['longitude']))
            panoids = panoids_from_response(resp.text)
            # print(panoids)
        except Exception as e:
            # print(e)
            continue
        if len(panoids)==0:
            continue
        for pano in panoids:
            try :
                year = int(pano['year'])
                month = int(pano['month'])
            except Exception as e :
                year = 0
                month = 0
            try :

                heading = pano['heading']
                panoid = pano['panoid']
                option1 = (heading + 90) % 360
                option2 = (heading + 180) % 360
                option3 = (heading + 270) % 360
                option4 = (heading + 0) % 360

                # for index, heading in enumerate([adjusted_90, adjusted_180]):
                    # Id_ = Id*2 + index
                # for heading in [adjusted_90, adjusted_180]:
                for option in [option1, option2, option3, option4]:
                    option =round(option, 1)   
                    img_save_path = output_+f"/{index}_{int(row['osm_id'])}_{row['longitude']}_{row['latitude']}_{option}_{year}_{month}.jpg"
                    if os.path.exists(img_save_path):
                        print("图像已存在，跳过保存:", img_save_path)
                        continue    

                    # 获取图像
                    img = get_streetview(panoid, 960, 720, 0, option)
                    if img is not None:
                        
                        # 保存到本地
                        img.save(img_save_path)
                        print("图像已保存为",img_save_path)
                    else:
                        print("未能获取图像")
                break
            except Exception as e :
                print(f'error:{e}')
                break
                continue

points_csv = r'e:\work\sv_gonhoo\_network_40m_unique_Spatial_Balance.csv'

zoom = 3
output_ = r'e:\work\sv_gonhoo\svi'

if os.path.exists(output_) == False:
    os.makedirs(output_)
main(points_csv,output_)
