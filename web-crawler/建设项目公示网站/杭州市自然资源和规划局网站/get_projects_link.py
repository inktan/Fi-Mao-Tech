import re
import requests
import pandas as pd
import os
from pathlib import Path

def extract_project_info(url, output_csv):
    # 发送HTTP请求获取网页内容
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    
    if response.status_code != 200:
        print(f"请求失败，状态码：{response.status_code}")
        return
    
    html_content = response.text
    
    # 使用正则表达式提取数据
    pattern = re.compile(
        r'<tr class="DGtable_item odd">.*?'
        r'<a href="(.*?)".*?title="(.*?)">.*?'
        r'<td align="left" class="td2">(.*?)</td>.*?'
        r'<td class="td3">.*?<span>(.*?)</span>.*?'
        r'<td class="td4">.*?<span>(.*?)</span>.*?'
        r'</tr>',
        re.DOTALL
    )
    
    matches = pattern.findall(html_content)
    
    # 整理新数据
    new_data = []
    existing_links = set()
    
    # 如果文件已存在，读取已有数据
    if os.path.exists(output_csv):
        existing_df = pd.read_csv(output_csv, encoding='utf-8-sig')
        existing_links = set(existing_df['项目名称'].tolist())
    else:
        existing_df = pd.DataFrame(columns=['项目名称', '公示类别', '公示日期', '截止日期', '链接'])

    for match in matches:
        link, project_name, category, publish_date, end_date = match

        clean_date = re.sub(r'\s+', '', publish_date.strip())
        # 提取年份
        try:
            year = int(clean_date[:4])  # 假设日期格式为"YYYY年MM月DD日"
        except (ValueError, IndexError):
            year = 0  # 日期格式不符合预期

        # 只添加新链接且年份>=2025的数据
        if project_name not in existing_links and year >= 2025:
            new_data.append({
                '项目名称': project_name.strip(),
                '公示类别': category.strip(),
                '公示日期': publish_date.strip(),
                '截止日期': end_date.strip(),
                '链接': link.strip()
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

# 使用示例
number_of_pages = 1
for page in range(1, number_of_pages + 1):
    if page > 1:
        # 构造URL
        url = f"https://ghzyj.sh.gov.cn/gszqyj/index_{page}.html"
    else:
        # 第一页的URL
        url = r"http://ghzy.hangzhou.gov.cn/col/col1228968050/index.html"

    output_csv = f"E:\\建设项目公示信息\\杭州\\杭州市\\建设项目公示信息表_2025.csv"
    extract_project_info(url, output_csv)
    # break
