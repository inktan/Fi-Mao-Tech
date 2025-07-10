import requests

def download_image(url, save_path):
    try:
        # 发送 HTTP GET 请求
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 检查请求是否成功
        
        # 以二进制写入模式打开文件
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"图片已成功下载到: {save_path}")
    except Exception as e:
        print(f"下载图片时出错: {e}")

# 示例用法
image_url = "https://streetviewpixels-pa.googleapis.com/v1/tile?cb_client=maps_sv.tactile&panoid=VmZCTNWG8b5fFVUbucXU9g&x=2&y=2&zoom=3&nbt=1&fover=2"  # 替换为你要下载的图片地址
save_location = "downloaded_image.jpg"      # 保存的文件名

download_image(image_url, save_location)