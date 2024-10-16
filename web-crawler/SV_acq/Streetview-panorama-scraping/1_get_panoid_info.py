import json
import math
import asyncio
import itertools
import traceback
import webbrowser
from pprint import pprint
import csv
from tqdm import tqdm

import aiohttp
import folium

import streetview


async def get_panoid(lat, lon, session):
    """ Get data about panoids asynchronously """
    try:
        url = f"https://maps.googleapis.com/maps/api/js/GeoPhotoService.SingleImageSearch?pb=!1m5!1sapiv3!5sUS!11m2!1m1!1b0!2m4!1m2!3d{lat}!4d{lon}!2d50!3m10!2m2!1sen!2sGB!9m1!1e2!11m4!1m3!1e2!2b1!3e2!4m10!1e1!1e2!1e3!1e4!1e8!1e6!5m1!1e2!6m1!1e2&callback=_xdc_._v2mub5"
        async with session.get(url) as resp:
            assert resp.status == 200
            text = await resp.text()
            panoids = streetview.panoids_from_response(text)
            all_panoids.extend(panoids)
    except:
        print('timeout')
        await asyncio.sleep(10)
        await get_panoid(lat, lon, session)


async def request_loop():
    conn = aiohttp.TCPConnector(limit=100)
    async with aiohttp.ClientSession(connector=conn) as session:
        try:
            await asyncio.gather(*[get_panoid(*point, session) for point in test_points])
        except:
            print(traceback.format_exc())


def distance(p1, p2):
    """ Haversine formula: returns distance for latitude and longitude coordinates"""
    R = 6373
    lat1 = math.radians(p1[0])
    lat2 = math.radians(p2[0])
    lon1 = math.radians(p1[1])
    lon2 = math.radians(p2[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R*c


if __name__ == "__main__":
    
    # 输入经纬度点的csv文件
    input = r'e:\work\sv_YJ_20240924\los_angeles_panoid_only_latest_year_unique_pano_id.csv'
    # 输入街景保存文件夹
    output_ = r'e:\work\sv_YJ_20240924\sv_pan02'
    output_csv = r'e:\work\sv_YJ_20240924\sv_test_info.csv'

    with open(input, 'r') as f:  
        reader = csv.reader(f)
        mylist = list(reader)
        count = 0
        # print(mylist)
        for row in tqdm(mylist):
            count += 1
            if count == 1 or len(row)<3:
                continue
            # if count <= 16890:
            #     continue
            # if count >300000005:
            #     continue
            lon = row[1]
            lat = row[0]

            test_points = [(lat,lon)]
            ### Show test points
            # for point in test_points:
            #     folium.Circle(location=point, radius=1, color='red').add_to(M)

            # Run asynchronous loop to get data about panos
            all_panoids = list()
            loop = asyncio.get_event_loop()
            loop.run_until_complete(request_loop())

            # Filter out duplicates
            print(f'Pre-filtering: {len(all_panoids)} panoramas')
            
            already_in = set()
            new_all_panoids = list()
            for pan in all_panoids:
                if not pan['panoid'] in already_in:
                    already_in.add(pan['panoid'])
                    new_all_panoids.append(pan)

            print(f'Post-filtering: {len(new_all_panoids)} panoramas')

            # Add points streetview locations
            for pan in new_all_panoids:
                folium.CircleMarker([pan['lat'], pan['lon']], popup=pan['panoid'], radius=1, color='blue', fill=True).add_to(M)

            # Save data
            with open(f'panoids_{len(new_all_panoids)}.json','w') as f:
                json.dump(new_all_panoids, f, indent=2)

            ## Save map and open it
            M.save(file)
            webbrowser.open(file)
