import re
import pandas as pd
import requests

def extract_data_with_regex(url, output_csv):
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
    
    # 准备数据列表
    data = []
    for match in matches:
        link, project_name, category, publish_date, end_date = match
        data.append([
            project_name.strip(),
            category.strip(),
            publish_date.strip(),
            end_date.strip(),
            link.strip()
        ])
    
    # 创建DataFrame并保存为CSV
    if data:
        print(f"找到 {len(data)} 条数据")
        df = pd.DataFrame(data, columns=['项目名称', '公示类别', '公示日期', '截止日期', '链接'])
        df.to_csv(output_csv, index=False, encoding='utf-8-sig')
        print(f"数据已成功保存到 {output_csv}")
    else:
        print("未找到匹配的数据")

# 使用示例
number_of_pages = 1
for page in range(1, number_of_pages + 1):
    # 构造URL
    url = f"http://ghzy.hangzhou.gov.cn/col/col1228968050/index.html"
    output_csv = f"project_data_page_{page}.csv"
    extract_data_with_regex(url, output_csv)