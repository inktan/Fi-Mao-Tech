import requests
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from urllib.parse import urljoin

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

def download_strava_heatmap_tiles(base_url, i_range, j_range, output_dir):
    """
    批量下载Strava热力图片
    
    Args:
        base_url: 基础URL模板
        i_range: i的范围，如range(27440, 27445)
        j_range: j的范围，如range(13385, 13390)
        output_dir: 输出目录
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 计数器
    success_count = 0
    fail_count = 0
    
    for i in i_range:
        for j in j_range:
            # 替换URL中的i和j
            url = base_url.replace('27442', str(i)).replace('13388', str(j))
            
            # 生成文件名
            filename = f"strava_heatmap_{i}_{j}.png"
            filepath = os.path.join(output_dir, filename)
            if os.path.exists(filepath):
                print(f"✓ 已存在，跳过: {filename}")
                success_count += 1
                continue
            
            try:
                # 发送请求
                # headers = {
                #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                # }
                response = requests.get(url, headers=headers, timeout=10)
                
                # 检查请求是否成功
                if response.status_code == 200:
                    # 保存图片
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    print(f"✓ 下载成功: {filename}")
                    success_count += 1
                else:
                    print(f"✗ 下载失败: {filename} - 状态码: {response.status_code}")
                    fail_count += 1
                    
            except Exception as e:
                print(f"✗ 下载错误: {filename} - 错误: {str(e)}")
                fail_count += 1
    
    print(f"\n下载完成! 成功: {success_count}, 失败: {fail_count}")

# 使用示例
if __name__ == "__main__":
    base_url = "https://content-a.strava.com/identified/globalheat/sport_Ride/purple/15/27442/13388.png?v=19"
    
    # 设置i和j的范围

    i_range = range(27415, 27465)  # i的范围
    j_range = range(13355, 13410)  # j的范围
    
    output_dir = r"E:\work\苏大-鹌鹑蛋好吃\20251015\strava_heatmaps"
    
    download_strava_heatmap_tiles(base_url, i_range, j_range, output_dir)