import csv
import time
from tqdm import tqdm
import time
import requests
import re
import requests
from requests.models import Response
import time
import pandas as pd  
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
    print("Parsing response...")
    print('length of text:',len(text))
    print(text[0:200])
    pans = re.findall('\[[0-9]+,"(.+?)"\].+?\[\[null,null,(-?[0-9]+\.[0-9]+),(-?[0-9]+\.[0-9]+).*?\],\s*\[(-?[0-9]+\.[0-9]+).*?\[(-?[0-9]+\.[0-9]+),(-?[0-9]+\.[0-9]+),(-?[0-9]+\.[0-9]+)\]', text)
    # pans = re.findall('\[[0-9]+,"(.+?)"\].+?\[\[null,null,(-?[0-9]+.[0-9]+),(-?[0-9]+.[0-9]+)', text)
    print('length of pans:',len(pans))
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
        if 'year'in x:
            return datetime(year=x['year'], month=x['month'], day=1)
        else:
            return datetime(year=3000, month=1, day=1)
    pans.sort(key=func)

    if closest:
        return [pans[i] for i in range(len(dates))]
    else:
        return pans

def main(samplesFeatureClass,output_):

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

        # print(index,float(row['longitude_circle']),float(row['latitude_circle']))
        print(df.shape)

        try:
            resp = search_request(float(row['latitude_circle']), float(row['longitude_circle']))
            panoids = panoids_from_response(resp.text)
        except Exception as e:
            print(e)
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
                # print(pano)
                # print(year)
                # print(month)

            with open(sv_infos_path,'a' ,newline='') as f:
                writer = csv.writer(f)
                writer.writerow([int(row['id']),int(row['id_circle']),
                float(row['longitude_circle']),
                float(row['latitude_circle']),
                pano['panoid'],
                pano['pitch'],
                pano['heading'],
                pano['fov01'],
                pano['fov02'],
                year, month])

                print(count)
                count+=1
                break

csv_path = r'e:\work\sv_j_ran\points\data_coor_unique_500_circle.csv' # 需要爬取的点
sv_infos_path = csv_path.replace('.csv','_sv_heading_infos_.csv')

with open(sv_infos_path,'w' ,newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['id','id_circle','longitude_circle','latitude_circle','panoid','pitch','heading','fov01','fov02','year','month'])

main(csv_path,sv_infos_path)
