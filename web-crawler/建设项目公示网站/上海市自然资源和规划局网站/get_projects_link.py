import re
import requests
import pandas as pd
import os
from pathlib import Path

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

        # 定义正则表达式模式（匹配h4和紧邻的div）
        pattern = r'''
            <h4>\s*<a\s+title="([^"]+)"\s+href="([^"]+)"[^>]*>.*?</a>\s*</h4>  # h4部分
            \s*<div\s+class="small\s+text-muted\s+mb-5">\s*<i[^>]*></i>\s*([^<]+)\s*</div>  # div部分
        '''
        
        # 查找所有匹配项
        matches = re.findall(pattern, html_content, re.VERBOSE)

        # 整理新数据
        new_data = []
        existing_links = set()
        
        # 如果文件已存在，读取已有数据
        if os.path.exists(output_csv):
            existing_df = pd.read_csv(output_csv, encoding='utf-8-sig')
            existing_links = set(existing_df['项目名称'].tolist())
        else:
            existing_df = pd.DataFrame(columns=['项目名称', '发布日期', '链接'])

        # 筛选新数据
        for title, href, date in matches:
            clean_date = re.sub(r'\s+', '', date.strip())
            
            # 提取年份
            try:
                year = int(clean_date[:4])  # 假设日期格式为"YYYY年MM月DD日"
            except (ValueError, IndexError):
                year = 0  # 日期格式不符合预期

            # 只添加新链接且年份>=2025的数据
            if href not in existing_links and year >= 2025:
                new_data.append({
                    '项目名称': title,
                    '发布日期': clean_date,
                    '链接': href
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
number_of_pages = 10
for page in range(1, number_of_pages + 1):
    if page > 1:
        # 构造URL
        url = f"https://ghzyj.sh.gov.cn/gszqyj/index_{page}.html"
    else:
        # 第一页的URL
        url = r"https://ghzyj.sh.gov.cn/gszqyj/index.html"

    output_csv = f"E:\\建设项目公示信息\\上海\\上海市\\建设项目公示信息表_2025.csv"
    extract_project_info(url, output_csv)
    # break
