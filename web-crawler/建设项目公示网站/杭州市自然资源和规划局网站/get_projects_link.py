import requests
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
import re
import os
import sys

# 获取当前文件的父目录的父目录（即上级目录）
parent_dir = str(Path(__file__).parent.parent)
sys.path.append(parent_dir)  # 将上级目录加入 Python 路径

# 现在可以直接导入上级目录的模块
from file_utils import get_deepest_dirs, create_safe_dirname, PROJECT_KEYWORDS

root_directory = r"Y:\\GOA-项目公示数据\\建设项目公示信息\\杭州\\杭州市"  # 替换为你的目标文件夹路径
deepest_dir_names = get_deepest_dirs(root_directory)

def make_pudong_gov_request(url):
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
    for match in matches:
        link, project_name, category, publish_date, end_date = match

        clean_date = re.sub(r'\s+', '', publish_date.strip())
        # 提取年份
        try:
            year = int(clean_date[:4])  # 假设日期格式为"YYYY年MM月DD日"
        except (ValueError, IndexError):
            year = 0  # 日期格式不符合预期

        # 只添加新链接且年份>=2025的数据
        if int(year) < 2025:
            continue
        if any(keyword in project_name for keywordin PROJECT_KEYWORDS):
            continue
        try:
            safe_dirname = create_safe_dirname(project_name, publish_date[:10])
            if safe_dirname in deepest_dir_names:
                # print(f"'{safe_dirname}' 已存在，跳过处理")
                continue
            project_dir = os.path.join(base_output_dir, safe_dirname)

            path = Path(project_dir)
            if path.exists() and path.is_dir():
                # print(f"文件夹 {project_dir} 已存在，跳过处理")
                continue
            os.makedirs(project_dir, exist_ok=True)
            # 设置输出文件路径
            csv_path = os.path.join(project_dir, "项目详情.csv")
            
            full_url = f"http://ghzy.hangzhou.gov.cn{link}"
            print(f"\n处理项目: {project_name}",f"项目URL: {full_url}")
            
            # 获取并保存项目信息
            extract_project_info(full_url, csv_path, project_dir, project_name)
        except Exception as e:
            print(f"处理项目 {project_name} 时出错: {str(e)}")
            continue

def extract_project_info(url, output_csv, img_dir, project_name):
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
    data = {
        "项目名称": get_text(soup, 'lblTeamName'),
        "建设单位": get_text(soup, 'lblBuildUnit'),
        "开始时间": get_text(soup, 'lblBeginDate'),
        "结束时间": get_text(soup, 'lblEndDate'),
        "来源URL": url
    }
    # 保存到CSV
    df = pd.DataFrame([data])
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"项目信息已保存到 {output_csv}")
    # 下载所有图片
    download_images(soup, img_dir, headers, project_name)

def get_text(soup, element_id):
    """安全获取元素文本"""
    element = soup.find('span', id=element_id)
    return element.text.strip() if element else ""

def download_images(soup, img_dir, headers, project_name):
    """下载页面中的所有图片"""
    img_count = 0
    for a_tag in soup.find_all('a', href=True, target='_blank'):
        if a_tag.find('img'):
            img_link = a_tag['href']
            base_url = r"https://zjjcmspublic.oss-cn-hangzhou-zwynet-d01-a.internet.cloud.zj.gov.cn/jcms_files/jcms1/web3390/site"
            full_img_url = base_url + img_link
            try:
                img_response = requests.get(full_img_url, headers=headers, stream=True, timeout=10)
                img_response.raise_for_status()
                url_imgname = os.path.basename(img_link)
                filename = project_name+'.'+url_imgname.split('.')[1]
                filename = '公示图'+'.'+url_imgname.split('.')[1]
                save_path = os.path.join(img_dir, filename)
                with open(save_path, 'wb') as f:
                    for chunk in img_response.iter_content(1024):
                        f.write(chunk)
                img_count += 1
                print(f"图片已保存: {save_path}")
            except Exception as e:
                print(f"下载图片失败: {full_img_url}, 错误: {e}")
    print(f"共下载 {img_count} 张图片")

# 使用示例
number_of_pages = 3
for page in range(1, number_of_pages + 1):
    if page > 1:
        # 构造URL
        url = f"https://ghzyj.sh.gov.cn/gszqyj/index_{page}.html"
    else:
        # 第一页的URL
        url = r"http://ghzy.hangzhou.gov.cn/col/col1228968050/index.html"

    base_output_dir = r"Y:\GOA-项目公示数据\建设项目公示信息\杭州\杭州市\未分类项目"
    print(url)
    make_pudong_gov_request(url)
    # break
