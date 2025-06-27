
import requests
import json
import time
from datetime import datetime

import os
from bs4 import BeautifulSoup
import re

def create_safe_dirname(project_name, publish_date):
    """创建安全的文件夹名称"""
    # 移除特殊字符
    project_name = re.sub(r'[\\/*?:"<>|]', "", project_name)
    publish_date = re.sub(r'[\\/*?:"<>|]', "", publish_date)
    # 合并为文件夹名
    dirname = f"{publish_date[:10]}_{project_name}"  # 只取日期部分
    return dirname[:180]  # 限制长度防止路径过长

main_url = "https://mp.weixin.qq.com/cgi-bin/appmsgpublish"

headers = {
    "Authority": "mp.weixin.qq.com",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Priority": "u=1, i",
    "Referer": "https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&isNew=1&type=77&createType=0&token=1825166898&lang=zh_CN&timestamp=1750328917785",
    "Sec-Ch-Ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

# cookies、token、fakeid，保存下来，这三者缺一不可

cookies = {
    "RK": "fCX0tqueWs",
    "ptcz": "7a473fcf51697bfc8b5f60a985ce8d0b00414a9e51fb375a399958d9fd27688a",
    "ua_id": "HMV7IE3np8vcDyIHAAAAAIMskFxnuPnsMuGxJzH7XPc=",
    "wxuin": "40479797108846",
    "mm_lang": "zh_CN",
    "pgv_pvid": "1704915140075719",
    "_t_qbtool_uid": "aaaaz2i556g4ttu1me7sikfqy0mp88cb",
    "_ga": "GA1.1.28274720.1743177134",
    "_ga_TPFW0KPXC1": "GS1.1.1743302505.2.0.1743302508.0.0.0",
    "fqm_pvqid": "adae4afe-e650-4e3c-9495-1592eb46efef",
    "b-user-id": "288c6bfa-76e7-63a1-0050-8b3cf7dba4f1",
    "poc_sid": "HH7dU2ijlQ3OrFZNKco8U_N2roQ1dhWy6lPP2jPY",
    "_qimei_uuid42": "19614103800100c93f8f8e424181aca54cabf3b0cc",
    "_qimei_fingerprint": "a4815e4bf7ad1377c7fed7fd89ffc136",
    "_qimei_q36": "",
    "_qimei_h38": "8f95affb3f8f8e424181aca502000009e19614",
    "qq_domain_video_guid_verify": "b938daed60480ff9806956192a301bf1",
    "rewardsn": "",
    "wxtokenkey": "777",
    "_clck": "3891696458|1|fx1|0",
    "uuid": "b6cb4b0105ad3a57101afbec59af22a0",
    "rand_info": "CAESIP1jP5hxEoC3zc/cwoumr5sI39Cl0wbadDs8iwFJOYUk",
    "slave_bizuin": "3891696458",
    "data_bizuin": "3891696458",
    "bizuin": "3891696458",
    "data_ticket": "Ocy4NTIWez2VKDsHUm0bfQPuCmG5Z06hqWzkNcvXtTDa0EFUVZ9RttWjJumLchwC",
    "slave_sid": "SjBkcVh1bmRrSHozN1RrcUZGMThGWWJFeUtfYmZRaTFGSkg5ZHdoNEc5bWJCakNGNk5tNkI4NmJnMlFDVHJtV3VlSzBoZjRzRmp6dUNjS1VrQzFDYUN5OGVOWWdtRE1ZY3B2ZEkxYlFYY2Z4WE40MmwydWlFYmRnaHFyTHhueDhlaVdKUHJzb0xBSW10TUlD",
    "slave_user": "gh_08417651a0c6",
    "xid": "376ff687b6cb941e492f502fb8c2eea6",
    "_clsk": "159jmzf|1750737967437|6|1|mp.weixin.qq.com/weheat-agent/payload/record"
}

params = {
    "sub": "list",
    "search_field": "null",
    "begin": "0",
    "count": "5",
    "query": "",
    "fakeid": "MzA5NDM4MzE2Nw==",
    "type": "101_1",
    "free_publish_type": "1",
    "sub_action": "list_ex",
    "fingerprint": "16daecebf52ee8530c267f299906bbb6",
    "token": "975399779",
    "lang": "zh_CN",
    "f": "json",
    "ajax": "1"
}

response = requests.get(
    main_url,
    headers=headers,
    cookies=cookies,
    params=params
)

parsed_data = json.loads(response.text)

publish_page_str = parsed_data["publish_page"]
publish_page_data = json.loads(publish_page_str)
print(publish_page_data['total_count'])
masssend_count = publish_page_data['masssend_count']

for i in range(0, masssend_count, 5):
    print(i)
    print(f"正在处理第{i//5 + 1}页数据...")
    
    params['begin'] = i

    response = requests.get(
        main_url,
        headers=headers,
        cookies=cookies,
        params=params
    )

    parsed_data = json.loads(response.text)

    publish_page_str = parsed_data["publish_page"]
    publish_page_data = json.loads(publish_page_str)

    publish_list = publish_page_data['publish_list']
    need_down = True
    for j in range(len(publish_list)):
        single_data = json.loads(publish_list[j]['publish_info'])

        create_time = single_data['appmsgex'][0]['create_time']
        dt = datetime.fromtimestamp(create_time)
        publish_date = dt.strftime("%Y年%m月%d日")
        year = dt.year

        if year < 2025:
            need_down = False
            break

        # print(single_data['sent_status']['total'])
        title = single_data['appmsgex'][0]['title']
        cover = single_data['appmsgex'][0]['cover']
        link = single_data['appmsgex'][0]['link']

        # 创建附图文件夹
        base_output_dir = r'Y:\GOA-项目公示数据\公众号\建筑芝士'
        safe_dirname = create_safe_dirname(title, publish_date)
        project_dir = os.path.join(base_output_dir, safe_dirname)
        image_folder = os.path.join(project_dir, '附图')
        if not os.path.exists(image_folder):
            os.makedirs(image_folder)
        else:
            print(f'文件夹已存在: {image_folder}')
            need_down = False
            break

        text_path = os.path.join(project_dir, '内容.txt')

        # 获取网页内容
        url = link
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取文字内容
        content_div = soup.find('div', id='img-content')
        if content_div:
            # 保存文字内容到txt文件
            text_content = content_div.get_text(separator='\n', strip=True)
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            
            # 提取并保存图片
            images = content_div.find_all('img')
            count = 1
            for i, img in enumerate(images, 1):
                img_url = img.get('data-src')
                if img_url and img_url.startswith('http'):
                    try:
                        img_data = requests.get(img_url).content
                        img_path = os.path.join(image_folder, f'附图{count}.jpg')
                        count += 1
                        
                        with open(img_path, 'wb') as img_file:
                            img_file.write(img_data)
                        print(f'保存图片: {img_path}')
                    except Exception as e:
                        print(f'下载图片失败: {img_url}, 错误: {e}')
        else:
            print('未找到id为img-content的div')

        print('处理完成')
        time.sleep(3)

    if not need_down:
        break
