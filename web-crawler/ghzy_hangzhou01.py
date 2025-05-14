import os
import pandas as pd

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from urllib.parse import urljoin

csv_path = r'e:\project_data_page_1.csv'

total_rows = 0
df = pd.read_csv(csv_path)
print(df.shape)
print(df.columns)
print(df.head())

def extract_project_info(url, output_csv, save_dir):
    # 发送HTTP请求
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        response.raise_for_status()  # 检查请求是否成功
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return

    # 解析HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 提取数据
    data = {
        "项目名称": soup.find('span', id='lblTeamName').text if soup.find('span', id='lblTeamName') else "",
        "建设单位": soup.find('span', id='lblBuildUnit').text if soup.find('span', id='lblBuildUnit') else "",
        "开始时间": soup.find('span', id='lblBeginDate').text if soup.find('span', id='lblBeginDate') else "",
        "结束时间": soup.find('span', id='lblEndDate').text if soup.find('span', id='lblEndDate') else ""
    }

    # 创建DataFrame并保存为CSV
    df = pd.DataFrame([data])
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"数据已保存到 {output_csv}")

    # 打印提取的数据
    print("提取的数据：")
    for key, value in data.items():
        print(f"{key}，{value}")

    # 查找图片链接
    img_link = None
    img_tag = soup.find('a', href=True, target='_blank')
    if img_tag and img_tag.find('img'):
        img_link = img_tag['href']
    
    if not img_link:
        print("未找到图片链接")
        return None
    
    # 拼接完整图片URL
    base_url = r"https://zjjcmspublic.oss-cn-hangzhou-zwynet-d01-a.internet.cloud.zj.gov.cn/jcms_files/jcms1/web3390/site"
    full_img_url = base_url + img_link
    print(f"完整图片URL: {full_img_url}")
    
    # 下载图片
    try:
        img_response = requests.get(full_img_url, headers=headers, stream=True)
        img_response.raise_for_status()
        
        # 从URL提取文件名
        filename = os.path.basename(img_link)
        save_path = os.path.join(save_dir, filename)
        
        # 保存图片
        with open(save_path, 'wb') as f:
            for chunk in img_response.iter_content(1024):
                f.write(chunk)
        
        print(f"图片已保存到: {save_path}")
        return save_path
    except Exception as e:
        print(f"下载图片失败: {e}")
        return None


save_dir = 'E:\\'
# 遍历'链接'列，添加前缀并打印
for link in df['链接']:
    full_url = f"http://ghzy.hangzhou.gov.cn{link}"
    print(full_url)

    output_csv = "project_details.csv"
    extract_project_info(full_url, output_csv,save_dir)
    break