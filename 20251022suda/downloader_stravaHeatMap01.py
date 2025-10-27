import requests
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

headers = {
            'authority': 'content-a.strava.com',
            'method': 'GET',
            'scheme': 'https',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'cache-control': 'no-cache',
            'cookie': 'sp=8d609c8e-2bb0-4dd3-812b-565b0fde7d36; _strava4_session=ev98m1l7d2eocv1i9pc8q72dh99rvbvo; CloudFront-Key-Pair-Id=K3VK9UFQYD04PI; CloudFront-Policy=eyJTdGF0ZW1lbnQiOiBbeyJSZXNvdXJjZSI6Imh0dHBzOi8vKmNvbnRlbnQtKi5zdHJhdmEuY29tL2lkZW50aWZpZWQvKiIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc2MTIwMzU5Mn19fV19; CloudFront-Signature=cZuzM5e~BWZ4JhGa2chpJV-d~UqU1JHQ~EWNZIJr5ds19QjrIaHzjCXnd6PdNq2riHgTKHTF8-pgGx6885rny-6B0htECFj1~L970p~aF~DQR3AG~e0LdMiqx8OGoeCkgfbJpJi1ythZNpFvGv1DpDH3b8BAtWshjusfua0k71UA2ull9CGkiPJ9SfQHpVMTduFr9MVCK7rDGgqQU-nLxR9bbmMcZRFQtpVOzm9KzIzbtEjP-zITS4HDiMQt-APMn1qktjyL0YlDZJOcPYDKD-0JznJHCkiXE7Ka0avHgVSTj-yALjbZE9lxItHGaIkwYChUVfQecW7BHIJIAhE3Mg__; _strava_idcf=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3NjEyMDM1OTIsImlhdCI6MTc2MTExNzE5MiwiYXRobGV0ZUlkIjoxNDI5NjA5OTcsInRpbWVzdGFtcCI6MTc2MTExNzE5Mn0.nd3Yo0wp9XbRUHpkswEF9R-1DEn49W5b5dX9861KqXM; _strava_CloudFront-Expires=1761203592000',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
            'referer': 'https://www.strava.com/'
        }

def download_single_tile(i, j, output_dir):
    """
    下载单个瓦片
    """
    # 构建URL - 使用字符串格式化
    url_template = "https://content-a.strava.com/identified/globalheat/sport_Ride/purple/15/{}/{}.png?v=19"
    url = url_template.format(i, j)
    
    filename = f"strava_heatmap_{i}_{j}.png"
    filepath = os.path.join(output_dir, filename)
    
    try:
        # headers = {
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        #     'Referer': 'https://www.strava.com/'
        # }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return True, filename, None
        else:
            return False, filename, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, filename, str(e)

def batch_download_parallel(i_range, j_range, output_dir, max_workers=5):
    """
    并行批量下载
    """
    os.makedirs(output_dir, exist_ok=True)
    
    success_count = 0
    fail_count = 0
    
    # 创建所有任务
    tasks = []
    for i in i_range:
        for j in j_range:
            tasks.append((i, j))
    
    print(f"开始下载 {len(tasks)} 个瓦片...")
    
    # 使用线程池并行下载
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_task = {
            executor.submit(download_single_tile, i, j, output_dir): (i, j) 
            for i, j in tasks
        }
        
        for future in as_completed(future_to_task):
            i, j = future_to_task[future]
            try:
                success, filename, error = future.result()
                if success:
                    print(f"✓ 下载成功: {filename}")
                    success_count += 1
                else:
                    print(f"✗ 下载失败: {filename} - {error}")
                    fail_count += 1
            except Exception as e:
                print(f"✗ 任务异常: {i}_{j} - {str(e)}")
                fail_count += 1
            
            # 添加延迟避免请求过于频繁
            time.sleep(0.1)
    
    print(f"\n下载统计:")
    print(f"成功: {success_count}")
    print(f"失败: {fail_count}")
    print(f"总计: {len(tasks)}")

# 使用示例
if __name__ == "__main__":
    # 定义下载范围

    i_range = range(27415, 27465)  # i的范围
    j_range = range(13355, 13410)  # j的范围
    
    output_dir = r"E:\work\苏大-鹌鹑蛋好吃\20251015\strava_heatmaps"
    
    # 串行下载
    # download_strava_heatmap_tiles(base_url, i_range, j_range, output_dir)
    
    # 并行下载（更快）
    batch_download_parallel(i_range, j_range, output_dir, max_workers=3)