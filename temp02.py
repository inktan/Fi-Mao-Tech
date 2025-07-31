import requests

url = "https://m.lianjia.com/sh/ershoufang/rs%E9%B9%8F%E7%A8%8B%E8%8B%91/?ticket=ST-16449581-Om98LpVV9eLNmq63gHb6Kzk0KqU-ke.com"

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Host": "m.lianjia.com",
    "Pragma": "no-cache",
    "Referer": "https://clogin.lianjia.com/",
    "Sec-Ch-Ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-site",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
}

cookies = {
    "lianjia_uuid": "61a30485-75d4-403f-a8cb-8949008e9ed6",
    "Hm_lvt_46bf127ac9b856df503ec2dbf942b67e": "1753933225",
    "HMACCOUNT": "2E252058C691871B",
    "_jzqa": "1.578712360721580200.1753933227.1753933227.1753933227.1",
    "_jzqc": "1",
    "_jzqy": "1.1753933227.1753933227.1.jzqsr=baidu|jzqct=%E9%93%BE%E5%AE%B6.-",
    "_jzqckmp": "1",
    "sajssdk_2015_cross_new_user": "1",
    "_ga": "GA1.2.354374190.1753933238",
    "_gid": "GA1.2.20226284.1753933238",
    "select_city": "310000",
    "crosSdkDT2019DeviceId": "rn5hdx--i8b8r9-fgqi6xr6g7i7ghp-ahf83ns5f",
    "ftkrc_": "6f59bc5a-c285-4b04-908b-b4a128c42997",
    "lfrc_": "a48c927c-70ba-44cd-b965-19055926137f",
    "_ga_LRLL77SF11": "GS2.2.s1753933316$o1$g1$t1753933321$j55$l0$h0",
    "_ga_GVYN2J1PCG": "GS2.2.s1753933316$o1$g1$t1753933321$j55$l0$h0",
    "Hm_lpvt_46bf127ac9b856df503ec2dbf942b67e": "1753933448",
    "sensorsdata2015jssdkcross": "%7B%22distinct_id%22%3A%221985e912e85266-0cb66a1141ab3c8-26011151-2073600-1985e912e86a9f%22%2C%22%24device_id%22%3A%221985e912e85266-0cb66a1141ab3c8-26011151-2073600-1985e912e86a9f%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_utm_source%22%3A%22baidu%22%2C%22%24latest_utm_medium%22%3A%22pinzhuan%22%2C%22%24latest_utm_campaign%22%3A%22wyhz%22%2C%22%24latest_utm_content%22%3A%22biaotimiaoshu%22%2C%22%24latest_utm_term%22%3A%22biaoti%22%7D%7D",
    "Hm_lvt_28b65c68923b952bf94c102598920ce0": "1753933531",
    "session_id": "2ca8cbb6-6602-866d-abf9-cae34a149803",
    "srcid": "eyJ0Ijoie1wiZGF0YVwiOlwiMmQwNTJlN2UxNWJiZGQ2MTcwMzRkOWNmZmUwNGJjNzc2NTAxZjAyMDc3Yzg5ODgxMTQ5ODU4NzlkM2JlMzdhNjFhYTc3ZjBiNTViYWUyMzRhMjE3YzdkYmIyZjE5MDhkZmY2ZTA0NDQ5ZjQyZTlhNDgzODI4MTY4YzdkYWFjZDY4NzllMWJlYTg2NGI2NGRjNmJlYjYwMjk5NDQ2Zjc1NWJlMmI2MGYwMjQ0MjNkN2NhMTY2ODk1MTIwYjQzM2U0N2VmY2E1ZjcwYjdmNDcwOTE4NjAzNTgzYmQ2NTNmY2I0NTE2NzAwN2U0MTVkMTBlNmU5ODMxYjViMmZlZjQwMFwiLFwia2V5X2lkXCI6XCIxXCIsXCJzaWduXCI6XCI4Y2E3YmUyNFwifSIsInIiOiJodHRwczovL20ubGlhbmppYS5jb20vc2gvZXJzaG91ZmFuZy9zZWFyY2gvIiwib3MiOiJ3ZWIiLCJ2IjoiMC4xIn0=",
    "_ga_XRDEC2G0T9": "GS2.2.s1753933532$o1$g1$t1753933796$j60$l0$h0",
    "_ga_XGP5EDPZTV": "GS2.2.s1753933532$o1$g1$t1753933796$j60$l0$h0",
    "_ga_SNG6R1B3VY": "GS2.2.s1753933532$o1$g1$t1753933796$j60$l0$h0",
    "digData": "%7B%22key%22%3A%22m_pages_ershoufangSearch%22%7D",
    "lianjia_ssid": "e2293963-4ec9-4268-97e2-e16037416b2c",
    "login_ucid": "2000000133679582",
    "lianjia_token": "2.001385d4e5711770d70228fdd46ff758fc",
    "lianjia_token_secure": "2.001385d4e5711770d70228fdd46ff758fc",
    "security_ticket": "mQtstzFmrTO9JO3+TwbIjhyCkK69hlVgpWjsBfe9wOyx1P7ra9uK5VsobVga1SqEOd6XUSHkknMNLcovZ1NgRJWGcyachc713heLZmWGr02jNfnZVRjIF3zj0/GRjq3e6QSRj72EXnUJ3RgLpgpWF8A9rW8smkqGiuWsIEY4/gk=",
    "Hm_lpvt_28b65c68923b952bf94c102598920ce0": "1753950334",
    "beikeBaseData": "%7B%22parentSceneId%22%3A%22%22%7D"
}

response = requests.get(url, headers=headers, cookies=cookies)

print(f"Status Code: {response.status_code}")
print("Response Headers:")
for header, value in response.headers.items():
    print(f"{header}: {value}")

# To see the response content (HTML)
# print(response.text)