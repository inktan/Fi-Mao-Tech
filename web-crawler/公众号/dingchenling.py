
import requests
import json
import time
from datetime import datetime

import os
from bs4 import BeautifulSoup
import re

from bs4 import BeautifulSoup
from docx import Document
from docx.shared import Inches
import requests
import io
from PIL import Image

def create_safe_dirname(project_name, publish_date):
    """创建安全的文件夹名称"""
    # 移除特殊字符
    project_name = re.sub(r'[\\/*?:"<>|]', "", project_name)
    publish_date = re.sub(r'[\\/*?:"<>|]', "", publish_date)
    # 合并为文件夹名
    dirname = f"{project_name[:100]}_{publish_date[:10]}"  # 只取日期部分
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
    "rewardsn": "",
    "wxtokenkey": "777",
    "poc_sid": "HH7dU2ijlQ3OrFZNKco8U_N2roQ1dhWy6lPP2jPY",
    "_clck": "hwsk3d|1|fww|0",
    "uuid": "80372cee90a3620ec5d86e584e93f982",
    "rand_info": "CAESIEJabpaOLuLdqP1lKj6OCvh6MI8hOekRagQ5f5/j6cjI",
    "slave_bizuin": "3891696458",
    "data_bizuin": "3891696458",
    "bizuin": "3891696458",
    "data_ticket": "yKc64NjfsvUfqI5xB40bVWwrm8MII+tFPWwC9vDqtUjQi7GqUesf72T/RZcvHflF",
    "slave_sid": "blBnb1ZUZUtTeFFaeHdwb1JyOUhJamowS19sb3ZzbVlTSWhDc242N0NudDdJWnRnTVVBN1FFWFZ2bDF4bE0xaUtVQ1duN2hmbVZETjlvZE1oa2FobzFBeFBlTzBtaFZsOWk4bVA4TjJvTEV4OWFYTXJkYWVrekphbmQ5cnlFVmZPVzhhUVJCMHQyenVNTTFW",
    "slave_user": "gh_08417651a0c6",
    "xid": "fa399642748836c8c79799fdd487db89",
    "_clsk": "1h22fl8|1750328919743|3|1|mp.weixin.qq.com/weheat-agent/payload/record"
}

params = {
    "sub": "list",
    "search_field": "null",
    "begin": "0",
    "count": "5",
    "query": "",
    "fakeid": "MjM5Njg1OTQ3Mg==",
    "type": "101_1",
    "free_publish_type": "1",
    "sub_action": "list_ex",
    "fingerprint": "038dd85112e63c99d3900811a884a257",
    "token": "1825166898",
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

for i in range(1045, masssend_count, 5):
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
    for j in range(len(publish_list)):
        # 安全获取并解析 JSON
        publish_info = publish_list[j].get('publish_info', '')
        if not publish_info.strip():
            print(f"Skipping empty data at index {j}")
            continue

        try:
            single_data = json.loads(publish_info)
        except json.JSONDecodeError:
            print(f"Skipping invalid JSON at index {j}")
            continue

        create_time = single_data['appmsgex'][0]['create_time']
        dt = datetime.fromtimestamp(create_time)
        publish_date = dt.strftime("%Y年%m月%d日")
        publish_year = dt.year
        publish_month = dt.month
        publish_day = dt.day

        # 如果日期小于2025年，则结束爬虫
        if publish_year < 2025:
            break

        # print(single_data['sent_status']['total'])
        title = single_data['appmsgex'][0]['title']
        cover = single_data['appmsgex'][0]['cover']
        link = single_data['appmsgex'][0]['link']

        illegal_chars = [" ", "/", "\\", "|", '"', ':', '*', '?', '<', '>', '|', '\t']
        for char in illegal_chars:
            title = title.replace(char, "_")

        # 创建附图文件夹
        base_output_dir = r'Y:\GOA-项目公示数据\公众号\建筑芝士'
        safe_dirname = create_safe_dirname(title, publish_date)
        project_dir = os.path.join(base_output_dir, safe_dirname)
        image_folder = os.path.join(project_dir, '附图')

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
            # 保存文字内容到word文件
            output_path = f'F:\\公众号\\丁辰灵\\{publish_date}_{title}.docx'
            output_path_img = f'F:\\公众号\\丁辰灵\\{publish_date}_{title}_img.docx'
                    
            if os.path.exists(output_path_img):
                continue  # 任一文件存在则跳过

            if not os.path.exists(image_folder):
                os.makedirs(image_folder)

            # 创建Word文档
            doc = Document()
            doc_img = Document()
                
            # 查找指定的div或使用整个body
            content_div = soup.find('div', id='img-content')
            content = content_div if content_div else soup.body
            
            # 处理所有元素
            for element in content.find_all(recursive=True):
                # 处理文本
                if element.name in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    doc.add_paragraph(element.get_text())
                    doc_img.add_paragraph(element.get_text())
                
                # 处理图片
                elif element.name == 'img':
                    img_url = element.get('data-src') or element.get('src')
                    if img_url:
                        try:
                            response = requests.get(img_url, stream=True)
                            if response.status_code == 200:
                                image = Image.open(io.BytesIO(response.content))
                                image_path = 'temp_image.jpg'
                                image.save(image_path)
                                doc_img.add_picture(image_path, width=Inches(4))
                        except:
                            pass  # 如果图片无法加载，跳过
            
            # 保存Word文档
            doc.save(output_path)
            doc_img.save(output_path_img)
            print(f"成功保存Word文件到: {output_path}")
            print(f"成功保存Word文件到: {output_path_img}")
            
        else:
            print('未找到id为img-content的div')

        print('处理完成')
        time.sleep(3)







