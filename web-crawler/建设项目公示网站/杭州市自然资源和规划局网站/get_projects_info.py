import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
from pathlib import Path

def create_safe_dirname(project_name, publish_date):
    """创建安全的文件夹名称"""
    # 移除特殊字符
    project_name = re.sub(r'[\\/*?:"<>|]', "", project_name)
    publish_date = re.sub(r'[\\/*?:"<>|]', "", publish_date)
    # 合并为文件夹名
    dirname = f"{project_name}_{publish_date[:10]}"  # 只取日期部分
    return dirname[:50]  # 限制长度防止路径过长

def process_project_data(row, base_output_dir="E:\\project_data"):
    """处理单条项目数据"""
    # 创建项目特定文件夹
    project_name = row['项目名称']
    publish_date = row['公示日期']
    
    try:
        safe_dirname = create_safe_dirname(project_name, publish_date)
        project_dir = os.path.join(base_output_dir, safe_dirname)

        path = Path(project_dir)
        if path.exists() and path.is_dir():
            print(f"文件夹 {project_dir} 已存在，跳过处理")
            return True  # 或者 continue 如果在循环中

        os.makedirs(project_dir, exist_ok=True)
        
        # 设置输出文件路径
        csv_path = os.path.join(project_dir, "项目详情.csv")
        # img_dir = os.path.join(project_dir, "images")
        img_dir = project_dir
        # os.makedirs(img_dir, exist_ok=True)
        
        # 构建完整URL
        full_url = f"http://ghzy.hangzhou.gov.cn{row['链接']}"
        print(f"\n处理项目: {project_name}")
        print(f"项目URL: {full_url}")
        
        # 获取并保存项目信息
        project_info = extract_project_info(full_url, csv_path, img_dir, project_name)
        
        return True
    except Exception as e:
        print(f"处理项目 {project_name} 时出错: {str(e)}")
        return False

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
    
    return data

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
            # full_img_url = urljoin(base_url, img_link)
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

# 主程序
if __name__ == "__main__":
    csv_path = r'e:\建设项目公示信息\杭州\杭州市\建设项目公示信息表_2025.csv'
    base_output_dir = r"e:\建设项目公示信息\杭州\杭州市\未分类项目"
    
    try:
        df = pd.read_csv(csv_path)
        print(f"共读取 {len(df)} 条项目数据")
        
        # 检查必要列是否存在
        required_columns = ['链接', '项目名称', '公示日期']
        if not all(col in df.columns for col in required_columns):
            raise ValueError("CSV文件中缺少必要的列")
        
        # 处理每条项目数据
        success_count = 0
        for _, row in df.iterrows():
            if process_project_data(row, base_output_dir):
                success_count += 1
                # break
        
        print(f"\n处理完成! 成功处理 {success_count}/{len(df)} 个项目")
    except Exception as e:
        print(f"程序运行出错: {str(e)}")