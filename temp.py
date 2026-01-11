import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# --- 配置参数 ---
html_path = r'C:\Users\wang.tan.GOA\Pictures\loopparade\content.html'
save_folder = r'C:\Users\wang.tan.GOA\Pictures\loopparade\downloaded_videos'
# 如果 mp4 的 src 是相对路径，需要提供一个基准 URL (如果是本地相对路径则设为原文件夹路径)
base_url = "" 

# 创建下载目录
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

def download_mp4_from_html():
    # 1. 读取本地 HTML 文件
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"错误：找不到文件 {html_path}")
        return

    # 2. 解析 HTML 寻找视频链接
    soup = BeautifulSoup(content, 'html.parser')
    video_links = []

    # 查找所有 video 标签和 source 标签
    sources = soup.find_all(['source', 'video'])
    for tag in sources:
        src = tag.get('src')
        if src and src.endswith('.mp4'):
            # 处理可能的相对路径
            full_url = urljoin(base_url, src) if base_url else src
            video_links.append(full_url)

    # 去重
    video_links = list(set(video_links))
    print(f"找到 {len(video_links)} 个视频链接。")

    # 3. 下载视频
    for url in video_links:
        file_name = os.path.basename(url).split('?')[0] # 移除 URL 参数
        file_path = os.path.join(save_folder, file_name)

        print(f"正在下载: {file_name} ...")
        
        try:
            # 如果是本地路径，直接复制文件；如果是网络链接，使用 requests
            if url.startswith('http'):
                response = requests.get(url, stream=True)
                response.raise_for_status()
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
            else:
                # 假设是本地相对路径，进行复制
                import shutil
                source_file = os.path.join(os.path.dirname(html_path), url)
                shutil.copy2(source_file, file_path)
                
            print(f"成功保存到: {file_path}")
        except Exception as e:
            print(f"下载失败 {url}: {e}")

if __name__ == "__main__":
    download_mp4_from_html()