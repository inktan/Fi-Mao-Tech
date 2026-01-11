import os
from rembg import remove
from PIL import Image

def process_rembg(input_root, output_root_name):
    """
    input_root: 输入的根目录路径
    output_root_name: 你想要替换掉的“父级的父级”的新文件夹名
    """
    
    # 遍历文件夹
    for root, dirs, files in os.walk(input_root):
        for filename in files:
            if filename.lower().endswith('.png'):
                # 1. 获取当前文件的完整路径
                input_path = os.path.join(root, filename)
                
                # 2. 计算输出路径
                # 假设路径是: ./frames/video1/frame_0001.png
                # 我们要把 'frames' 替换为 output_root_name (比如 'transparent_frames')
                relative_path = os.path.relpath(input_path, os.path.dirname(input_root))
                path_parts = relative_path.split(os.sep)
                
                # 替换顶层文件夹名
                path_parts[0] = output_root_name
                output_path = os.path.join(os.path.dirname(input_root), *path_parts)
                
                # 创建输出文件夹
                output_dir = os.path.dirname(output_path)
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                print(f"正在处理: {filename} -> {output_path}")

                # 3. 执行抠图
                try:
                    with open(input_path, 'rb') as i:
                        input_image = i.read()
                        # 使用 rembg 移除背景
                        output_image = remove(input_image)
                        
                        with open(output_path, 'wb') as o:
                            o.write(output_image)
                except Exception as e:
                    print(f"处理 {filename} 出错: {e}")

# --- 配置参数 ---
# 假设你的结构是 ./frames/video_name/*.png
# 执行后会生成 ./transparent_frames/video_name/*.png
input_folder = r"C:\Users\wang.tan.GOA\Pictures\loopparade\frames"            # 原始图片根目录
output_folder_name = r"transparent_frames"  # 新的父级文件夹名

process_rembg(input_folder, output_folder_name)
print("所有图片处理完成！")