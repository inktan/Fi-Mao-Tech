import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from scipy.ndimage import map_coordinates
import time

def project_image_to_cylinder(image_path, output_path='cylinder_projection.png', 
                             azimuth=30, elevation=30, height=2, radius=1, resolution=800):
    """
    优化版的圆柱体图片投影(使用向量化操作)
    
    参数:
    image_path - 输入图片路径
    output_path - 输出图片路径
    azimuth - 左右旋转角度(0-360)
    elevation - 上下俯视角度(0-90)
    height - 圆柱体高度
    radius - 圆柱体半径
    resolution - 圆柱体曲面分辨率
    """
    # 1. 加载图片
    img = Image.open(image_path)
    img_width, img_height = img.size
    img_array = np.array(img)  # shape: (height, width, 3)
    
    # 2. 准备圆柱体网格(向量化操作)
    theta = np.linspace(0, 2*np.pi, resolution)
    z = np.linspace(0, height, resolution)
    theta_grid, z_grid = np.meshgrid(theta, z)
    
    # 3. 坐标转换(向量化)
    u = (theta_grid / (2*np.pi)) * img_width
    v = (1 - z_grid/height) * img_height
    
    # 4. 使用map_coordinates进行高效采样
    # 将坐标转换为map_coordinates需要的格式
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
    
    # 6. 计算圆柱体表面坐标
    x = radius * np.cos(theta_grid)
    y = radius * np.sin(theta_grid)
    
    # 7. 绘制贴图圆柱体
    ax.plot_surface(x, y, z_grid, facecolors=colors,rstride=1, cstride=1,shade=False, antialiased=True)
    # 8. 隐藏坐标轴和设置比例
    ax.set_axis_off()
    max_range = max(radius*2, height)
    ax.set_xlim([-max_range/2, max_range/2])
    ax.set_ylim([-max_range/2, max_range/2])
    ax.set_zlim([0, max_range])
    ax.set_box_aspect([1, 1, height/(radius*2)])
    
    # 9. 调整边距并保存
    plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
    plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0, transparent=True)
    plt.close()
    print(f"圆柱体投影图已保存为 {output_path}")

# 示例使用
if __name__ == "__main__":
    input_image = r"e:\work\sv_huang_g\test\cylinder_sphere\10512_ss_svf_mask.png"
   
    start_time = time.perf_counter()
    for azimuth in [0,90,180,270]:
        output_image = f'e:/work/sv_huang_g/test/cylinder_sphere/10512_ss_svf_mask_cylinder_{azimuth}.png'
        project_image_to_cylinder(input_image, output_image,azimuth=azimuth, elevation=20,height=3.5, radius=1.45)
    
    # 结束计时
    elapsed = time.perf_counter() - start_time
    print(f"耗时: {elapsed:.3f}s")



