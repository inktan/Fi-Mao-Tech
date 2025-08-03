import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from scipy.ndimage import map_coordinates
import time

def project_image_to_sphere(image_path, output_path='sphere_projection.png', 
                           azimuth=30, elevation=30, radius=1, resolution=800):
    """
    将图片投影到球体的上半部分(修正上下颠倒问题)
    
    参数:
    image_path - 输入图片路径
    output_path - 输出图片路径
    azimuth - 左右旋转角度(0-360)
    elevation - 上下俯视角度(0-90)
    radius - 球体半径
    resolution - 球体曲面分辨率
    """
    # 1. 加载图片
    img = Image.open(image_path)
    img_width, img_height = img.size
    
    img = img.crop((0, 0, img_width, img_height // 2))
    img_width, img_height = img.size
        
    img_array = np.array(img)  # shape: (height, width, 3)
    
    # 2. 准备球体网格(仅上半部分)
    theta = np.linspace(0, 2*np.pi, resolution)  # 经度
    phi = np.linspace(0, np.pi/2, resolution)    # 纬度(仅上半球)
    theta_grid, phi_grid = np.meshgrid(theta, phi)
    
    # 3. 坐标转换(向量化) - 修改v坐标映射，解决上下颠倒问题
    u = (theta_grid / (2*np.pi)) * img_width
    v = (phi_grid / (np.pi/2)) * img_height  # 修改这里，去掉1-
    
    # 4. 使用map_coordinates进行高效采样
    coords = np.array([v.ravel(), u.ravel()])  # 注意y坐标在前
    
    # 对每个颜色通道分别采样
    channels = []
    for channel in range(3):  # RGB三个通道
        sampled = map_coordinates(img_array[:,:,channel], coords, order=1, mode='wrap')
        channels.append(sampled.reshape(resolution, resolution))
    
    # 组合颜色通道并归一化
    colors = np.dstack(channels) / 255.0
    colors = np.concatenate([colors, np.ones((resolution, resolution, 1))], axis=2)  # 添加alpha通道
    
    # 5. 创建3D图形
    fig = plt.figure(figsize=(10, 8), facecolor='white')
    ax = fig.add_subplot(111, projection='3d')
    ax.view_init(elev=elevation, azim=azimuth)
    
    # 6. 计算球体表面坐标
    x = radius * np.sin(phi_grid) * np.cos(theta_grid)
    y = radius * np.sin(phi_grid) * np.sin(theta_grid)
    z = radius * np.cos(phi_grid)
    
    # 7. 绘制贴图球体
    ax.plot_surface(x, y, z, facecolors=colors, rstride=1, cstride=1, 
                   shade=False, antialiased=True)
    
    # 8. 隐藏坐标轴和设置比例
    ax.set_axis_off()
    ax.set_xlim([-radius, radius])
    ax.set_ylim([-radius, radius])
    ax.set_zlim([0, radius])
    ax.set_box_aspect([1, 1, 0.5])  # 因为是上半球，z轴范围减半
    
    # 9. 调整边距并保存
    plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
    plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0, transparent=True)
    plt.close()
    print(f"球体投影图已保存为 {output_path}")

# 示例使用
if __name__ == "__main__":
    input_image = r"D:\Users\mslne\Documents\GitHub\Fi-Mao-Tech\sviPan2Cyli\temp\10512.jpg"
   
    start_time = time.perf_counter()
    for azimuth in [0, 90, 180, 270]:
        output_image = f'D:/Users/mslne/Documents/GitHub/Fi-Mao-Tech/sviPan2Cyli/temp/custom_sphere_{azimuth}.png'
        project_image_to_sphere(input_image, output_image, azimuth=azimuth, elevation=0, radius=1.5)
    
    # 结束计时
    elapsed = time.perf_counter() - start_time
    print(f"耗时: {elapsed:.3f}s")