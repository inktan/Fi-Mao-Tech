import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
from pathlib import Path

def get_deepest_dirs(root_dir):
    """获取所有嵌套最底层的文件夹路径（没有子文件夹的文件夹）"""
    deepest_dirs = set()

    for dirpath, dirnames, filenames in os.walk(root_dir):
        if not dirnames:  # 如果没有子文件夹，说明是底层文件夹
            dir_name = os.path.basename(dirpath)  # 获取文件夹名（不含路径）
            deepest_dirs.add(dir_name)

    return deepest_dirs
root_directory = r"Y:\GOA-项目公示数据\建设项目公示信息\上海\闵行区"  # 替换为你的目标文件夹路径
deepest_dir_names = get_deepest_dirs(root_directory)

def create_safe_dirname(project_name, publish_date):
    """创建安全的文件夹名称"""
    # 移除特殊字符
    project_name = re.sub(r'[\\/*?:"<>|]', "", project_name)
    publish_date = re.sub(r'[\\/*?:"<>|]', "", publish_date)
    # 合并为文件夹名
    dirname = f"{project_name}_{publish_date[:10]}"  # 只取日期部分
    return dirname[:100]  # 限制长度防止路径过长

def process_project_data(row, base_output_dir):
    """处理单条项目数据"""
    # 创建项目特定文件夹
    project_name = row['项目名称']
    publish_date = row['发布日期']
        
    try:
        safe_dirname = create_safe_dirname(project_name, publish_date)

        if safe_dirname in deepest_dir_names:
            print(f"'{project_name}' 已存在，跳过处理")
            return False
        
        project_dir = os.path.join(base_output_dir, safe_dirname)
        
        path = Path(project_dir)
        if path.exists() and path.is_dir():
            print(f"文件夹 {project_dir} 已存在，跳过处理")
            return True  # 或者 continue 如果在循环中
        
        os.makedirs(project_dir, exist_ok=True)
        
        # 设置输出文件路径
        # output_file = os.path.join(project_dir, "项目详情.csv")
        output_file = os.path.join(project_dir, "项目详情.txt")
        # img_dir = os.path.join(project_dir, "images")
        img_dir = project_dir
        os.makedirs(img_dir, exist_ok=True)
        
        # 构建完整URL
        # full_url = f"https://ghzyj.sh.gov.cn/{row['链接']}"
        full_url = row['链接']

        print(f"\n处理项目: {project_name}")
        print(f"项目URL: {full_url}")
        
        # 获取并保存项目信息
        # project_info = extract_project_info(full_url, output_file, img_dir, project_name)
        extract_project_info(full_url, output_file, img_dir, project_name)
        
        return True
    except Exception as e:
        print(f"处理项目 {project_name} 时出错: {str(e)}")
        return False

def extract_project_info(url, output_file, img_dir, project_name):
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
    download_pdf_attachments(soup, img_dir)
    
    # 提取基本信息
    # 查找id="ivs_content"的标签
    # content_div = soup.find(id="ivs_content")
    content_div = soup.find(class_="xx_text1")
    if not content_div:
        print("未找到id='ivs_content'的标签")
        return False

    # 获取所有文本内容（去除多余空白）
    content = content_div.get_text(separator='\n', strip=True)
    # 保存到txt文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"内容已保存到 {output_file}")

def download_pdf_attachments(soup, save_dir):
        # 查找所有class="xx_attach"的元素
    attachments = soup.find_all(class_="xx_attach")
    
    downloaded_files = []
    
    for i, attachment in enumerate(attachments, 1):
        # 查找PDF链接
        pdf_links = attachment.find_all('a', href=lambda x: x and x.lower().endswith('.pdf'))
        
        for link in pdf_links:
            pdf_url = link.get('href')
            pdf_download_name = link.get('download')
            if not pdf_url:
                continue
                
            # 构建完整URL
            full_url = urljoin(r'https://zwgk.shmh.gov.cn/', pdf_url)
            
            # 生成保存文件名
            # file_name = f"attachment_{i}_{os.path.basename(pdf_url)}"
            file_name = pdf_download_name
            save_path = os.path.join(save_dir, file_name)
            
            try:
                # 下载PDF文件
                response = requests.get(full_url, stream=True)
                response.raise_for_status()
                
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                downloaded_files.append(save_path)
                print(f"已下载: {file_name} (来自: {full_url})")
                
            except Exception as e:
                print(f"下载 {pdf_url} 失败: {e}")
    
    return downloaded_files

# 主程序
if __name__ == "__main__":
    csv_path = r'Y:\GOA-项目公示数据\建设项目公示信息\上海\闵行区\建设项目公示信息表_2025.csv'
    base_output_dir = r"Y:\GOA-项目公示数据\建设项目公示信息\上海\闵行区\未分类项目"
    
    try:
        df = pd.read_csv(csv_path)
        print(f"共读取 {len(df)} 条项目数据")
        
        # 检查必要列是否存在
        required_columns = ['链接', '项目名称', '发布日期']
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





