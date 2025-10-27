import requests
import os
import time
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

class StravaHeatmapDownloader:
    def __init__(self, output_dir="strava_heatmaps"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def download_tile(self, i, j, retry_count=3):
        """下载单个瓦片，支持重试"""
        url = f"https://content-a.strava.com/identified/globalheat/sport_Ride/purple/15/{i}/{j}.png?v=19"
        filename = f"strava_heatmap_{i}_{j}.png"
        filepath = os.path.join(self.output_dir, filename)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.strava.com/',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8'
        }
        
        for attempt in range(retry_count):
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    return True, filename
                elif response.status_code == 404:
                    # 该瓦片不存在
                    return False, f"{filename} - 不存在"
                else:
                    if attempt < retry_count - 1:
                        time.sleep(1)  # 重试前等待
                        continue
                    return False, f"{filename} - HTTP {response.status_code}"
                    
            except requests.exceptions.Timeout:
                if attempt < retry_count - 1:
                    time.sleep(1)
                    continue
                return False, f"{filename} - 超时"
            except Exception as e:
                if attempt < retry_count - 1:
                    time.sleep(1)
                    continue
                return False, f"{filename} - {str(e)}"
        
        return False, f"{filename} - 重试次数用尽"

    def batch_download(self, i_range, j_range, max_workers=3):
        """批量下载瓦片"""
        tasks = []
        for i in i_range:
            for j in j_range:
                tasks.append((i, j))
        
        print(f"准备下载 {len(tasks)} 个瓦片...")
        
        success_count = 0
        fail_count = 0
        
        # 使用进度条
        with tqdm(total=len(tasks), desc="下载进度") as pbar:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_task = {
                    executor.submit(self.download_tile, i, j): (i, j) 
                    for i, j in tasks
                }
                
                for future in as_completed(future_to_task):
                    i, j = future_to_task[future]
                    success, result = future.result()
                    
                    if success:
                        success_count += 1
                        pbar.set_postfix_str(f"成功: {success_count}, 失败: {fail_count}")
                    else:
                        fail_count += 1
                        # 只在失败时显示详细信息
                        tqdm.write(f"失败: {result}")
                    
                    pbar.update(1)
                    time.sleep(0.05)  # 控制请求频率
        
        print(f"\n下载完成!")
        print(f"成功: {success_count}")
        print(f"失败: {fail_count}")
        print(f"保存路径: {os.path.abspath(self.output_dir)}")

# 使用示例
if __name__ == "__main__":
    downloader = StravaHeatmapDownloader(r"E:\work\苏大-鹌鹑蛋好吃\20251015\strava_heatmaps")
    
    # 设置下载范围
    i_range = range(27440, 27445)  # i从27440到27444
    j_range = range(13385, 13390)  # j从13385到13389
    
    # 开始下载
    downloader.batch_download(i_range, j_range, max_workers=3)