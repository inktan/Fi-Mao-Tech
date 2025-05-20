import re
import requests
import pandas as pd
import os
from pathlib import Path
from bs4 import BeautifulSoup

def create_safe_dirname(project_name, publish_date):
    """创建安全的文件夹名称"""
    # 移除特殊字符
    project_name = re.sub(r'[\\/*?:"<>|]', "", project_name)
    publish_date = re.sub(r'[\\/*?:"<>|]', "", publish_date)
    # 合并为文件夹名
    dirname = f"{project_name}_{publish_date[:10]}"  # 只取日期部分
    return dirname[:100]  # 限制长度防止路径过长

def make_pudong_gov_request():
    # 设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # 目标URL
    url = "http://zrzy.jiangsu.gov.cn/gtapp/nrglIndex.action"  # 替换为实际的目标URL

    # Query String Parameters (查询字符串参数)
    query_params = {
        "classID": "2c9082b58db73afd018dc56f5b7e0491",
        "type": "1"
    }
    date_stop = False
    for i in range(10):
        try:
            if date_stop:
                break
            form_data = {
                "cpage": i+1
            }

            # 发送POST请求
            response = requests.post(
                url,
                params=query_params,  # 查询字符串参数
                data=form_data,       # 表单数据
                headers=headers       # 请求头
            )

            response.raise_for_status()
            html_content = response.text

            print(f"正在处理页面: {url}")
            # return
            # 解析HTML
            soup = BeautifulSoup(html_content, 'html.parser')
                        
            # 1. 找到目标div
            target_div = soup.find('div', class_='w780 xxgk-right')
            if not target_div:
                raise ValueError("未找到 class='w780 xxgk-right' 的div")
                
            # 2. 在div中查找tbody
            # 需要找到包含数据的tbody（跳过前面的导航和搜索表单的tbody）
            all_tbodies = target_div.find_all('tbody')

            # 通常数据表格是最后一个或倒数第二个tbody
            data_tbody = None
            for tbody in reversed(all_tbodies):
                # 检查tbody是否包含数据行（有索引号、名称、发布日期的列）
                if tbody.find('th', string='索引号') and tbody.find('th', string='名称'):
                    data_tbody = tbody
                    break

            if not data_tbody:
                raise ValueError("未找到包含数据的tbody")
                            
            for row in data_tbody.find_all('tr')[1:]:  # 跳过第一个tr（表头）
                cols = row.find_all('td')
                # print(cols)
                if len(cols) >= 3:  # 确保有3列数据
                    index_num = cols[0].get_text(strip=True)  # 索引号
                    publish_date = cols[2].get_text(strip=True)      # 发布日期

                    a_tag = cols[1].find('a')
                    project_name = a_tag.get('title')
                    pro_url = a_tag.get('href')

                    # 提取年份
                    try:
                        year = int(publish_date[:4])  # 假设日期格式为"YYYY年MM月DD日"
                    except (ValueError, IndexError):
                        year = 0  # 日期格式不符合预期

                    if int(year) < 2025:
                        date_stop = True
                        break

                    # 只添加新链接且年份>=2025的数据
                    if year >= 2025:
                        safe_dirname = create_safe_dirname(project_name, publish_date)
                        project_dir = os.path.join(base_output_dir, safe_dirname)
                        path = Path(project_dir)
                        if path.exists() and path.is_dir():
                            print(f"文件夹 {project_dir} 已存在，跳过处理")
                            # return True  # 或者 continue 如果在循环中
                            continue
                        os.makedirs(project_dir, exist_ok=True)
                        
                        # 设置输出文件路径
                        output_file = os.path.join(project_dir, "项目详情.txt")
                        
                        full_url = r'https://zrzy.jiangsu.gov.cn/' + pro_url
                        print(full_url)
                        extract_project_info(full_url,project_dir, output_file)

        except Exception as e:
            print(f"发生错误: {e}")
            return pd.DataFrame()

def extract_project_info(url, project_dir, output_file):
    """提取项目信息并下载图片"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 提取基本信息
    # 查找id="ivs_content"的标签
    # content_div = soup.find(id="Zoom")
    content_div = soup.find(class_="xxgk-gjy-top")
    if not content_div:
        print("未找到id='Zoom'的标签")
        return False

    # 获取所有文本内容（去除多余空白）
    content = content_div.get_text(separator='\n', strip=True)
    # 保存到txt文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"内容已保存到 {output_file}")
    # return

    # 初始化计数器
    image_counter = 1
    
    for img in soup.find_all('img', src=True):
        src = img['src']
        if 'attached' in src.lower():  # 不区分大小写匹配
            file_url = r'https://zrzy.jiangsu.gov.cn' + src
            try:
                # 获取文件
                response = requests.get(file_url,headers=headers,  stream=True)
                response.raise_for_status()
                
                # 获取文件名和扩展名
                if 'content-disposition' in response.headers:
                    # 从响应头获取文件名
                    filename = response.headers['content-disposition'].split('filename=')[-1].strip('"\'')
                else:
                    # 从 URL 获取文件名
                    filename = os.path.basename(file_url.split('?')[0])
                
                # 获取文件扩展名
                _, ext = os.path.splitext(filename.lower())
                ext = ext.lower()
                
                # 根据文件类型确定保存文件名
                if ext in ('.jpg', '.jpeg', '.png', '.gif', '.bmp'):
                    # 图片文件命名为 公示图01, 公示图02...
                    new_filename = f"公示图{image_counter:02d}{ext}"
                    image_counter += 1
                
                # 保存文件
                save_path = os.path.join(project_dir, new_filename)
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                
                print(f"已下载: {new_filename}")
                
            except Exception as e:
                print(f"下载 {file_url} 失败: {e}")

# 使用示例
base_output_dir = f"Y:\\GOA-项目公示数据\\建设项目公示信息\\苏州\\高新区\\未分类项目"
make_pudong_gov_request()
