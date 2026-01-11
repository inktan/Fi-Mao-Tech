import cv2
import os

def video_to_frames(input_dir, output_root):
    # 1. 检查并创建输出根目录
    if not os.path.exists(output_root):
        os.makedirs(output_root)

    # 2. 遍历输入文件夹中的所有文件
    for filename in os.listdir(input_dir):
        if filename.endswith(".mp4"):
            video_path = os.path.join(input_dir, filename)
            
            # 创建该视频专属的文件夹（去除.mp4后缀）
            video_name = os.path.splitext(filename)[0]
            video_output_dir = os.path.join(output_root, video_name)
            
            if not os.path.exists(video_output_dir):
                os.makedirs(video_output_dir)
            
            print(f"正在处理视频: {filename}...")
            
            # 3. 读取视频并逐帧保存
            cap = cv2.VideoCapture(video_path)
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break  # 视频读取完毕
                
                # 构建图片文件名，如 frame_0001.png
                frame_filename = os.path.join(video_output_dir, f"frame_{frame_count:04d}.png")
                
                # 保存图片
                cv2.imwrite(frame_filename, frame)
                frame_count += 1
            
            cap.release()
            print(f"完成！共导出 {frame_count} 张图片到 {video_output_dir}")

# --- 配置路径 ---
input_folder = r"C:\Users\wang.tan.GOA\Pictures\loopparade\downloaded_videos"      # 存放 mp4 的文件夹路径
output_folder = r"C:\Users\wang.tan.GOA\Pictures\loopparade\frames"     # 导出序列帧的根目录路径

video_to_frames(input_folder, output_folder)