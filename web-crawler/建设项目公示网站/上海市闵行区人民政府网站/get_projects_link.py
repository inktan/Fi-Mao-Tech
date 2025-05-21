import pandas as pd
import os
from pathlib import Path
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def extract_project_info(url,output_csv):
    try:
        # 设置请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 获取网页内容
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html_content = response.text

        # 整理新数据
        new_data = []
        existing_links = set()
        
        # 如果文件已存在，读取已有数据
        if os.path.exists(output_csv):
            existing_df = pd.read_csv(output_csv, encoding='utf-8-sig')
            existing_links = set(existing_df['项目名称'].tolist())
        else:
            existing_df = pd.DataFrame(columns=['项目名称', '发布日期', '链接'])

        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(html_content, 'html.parser')
                
        # 查找所有符合条件的<li>标签
        results = []
        for li in soup.find_all('li'):
            # 查找日期span
            date_span = li.find('span', class_='f_float')
            if not date_span:
                continue
                
            # 查找链接a标签
            a_tag = li.find('a', target='_blank')
            if not a_tag:
                continue
                
            # 提取信息
            date = date_span.get_text(strip=True)
            title = a_tag.get('title', '').strip()
            href = a_tag.get('href', '').strip()
            
            # 构建完整URL
            full_url = urljoin(url, href)

            clean_date = re.sub(r'\s+', '', date.strip())
            # 提取年份
            try:
                year = int(clean_date[:4])  # 假设日期格式为"YYYY年MM月DD日"
            except (ValueError, IndexError):
                year = 0  # 日期格式不符合预期
            
            if title not in existing_links and year >= 2025:
                new_data.append({
                    '项目名称': title,
                    '发布日期': clean_date,
                    '链接': full_url
                })

        if not new_data:
            print("没有发现新数据，CSV文件未更新")
            return existing_df

        # 合并新旧数据
        new_df = pd.DataFrame(new_data)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)

        # 确保输出目录存在
        output_path = Path(output_csv)
        output_dir = output_path.parent
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
            print(f"已创建目录: {output_dir}")

        # 保存为CSV
        combined_df.to_csv(output_csv, index=False, encoding='utf-8-sig')
        
        print(f"新增 {len(new_df)} 条数据，总计 {len(combined_df)} 条数据，已保存到 {output_csv}")
        return combined_df

    except Exception as e:
        print(f"发生错误: {e}")
        return pd.DataFrame()

# 使用示例
for page in [0,140,139,138,137,136,135,134,133,132,131]:
    url = f"https://zwgk.shmh.gov.cn/mh-xxgk-cms/website/mh_xxgk/xxgk_ghj_ywxx_ghglgs/List/list_{page}.htm"
    print(url)

    output_csv = f"Y:\\GOA-项目公示数据\\建设项目公示信息\\上海\\闵行区\\建设项目公示信息表_2025.csv"
    extract_project_info(url, output_csv)
    # break
