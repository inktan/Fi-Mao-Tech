import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from scipy.ndimage import map_coordinates
import time

def project_image_to_cylinder_optimized(image_path, output_path='cylinder_projection.png', 
                                      azimuth=30, elevation=30, height=2, radius=1, resolution=800):
    """
    高效版的圆柱体图片投影（通过2D投影替代3D渲染）
    """
    # 1. 加载图片
    img = Image.open(image_path)
    img_width, img_height = img.size
    img_array = np.array(img) / 255.0  # 直接归一化

    # 2. 生成圆柱体展开的UV坐标（向量化）
    theta = np.linspace(0, 2*np.pi, resolution)
    z = np.linspace(0, height, resolution)
    theta_grid, z_grid = np.meshgrid(theta, z)

    # 3. 坐标映射
    u = (theta_grid / (2*np.pi)) * img_width
    v = (1 - z_grid/height) * img_height

    # 4. 采样图像颜色（优化版）
    coords = np.array([v.ravel(), u.ravel()])
    channels = []
    for channel in range(3):
        sampled = map_coordinates(img_array[:,:,channel], coords, order=1, mode='wrap')
        channels.append(sampled.reshape(resolution, resolution))
    colors = np.dstack(channels)

    # 5. 直接绘制2D展开图并保存（跳过3D渲染）
    fig, ax = plt.subplots(figsize=(10, 8), facecolor='none')
    ax.set_axis_off()
    ax.imshow(colors, origin='lower', extent=[0, 2*np.pi*radius, 0, height], aspect='auto')
    
    # 6. 保存为透明背景图片
    plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0, transparent=True)
    plt.close()
    print(f"优化版圆柱体投影图已保存为 {output_path}")

# 示例使用
if __name__ == "__main__":
    input_image = r"D:\Users\mslne\Documents\GitHub\Fi-Mao-Tech\sviPan2Cyli\temp\10512.jpg"
    output_image = r'D:\Users\mslne\Documents\GitHub\Fi-Mao-Tech\sviPan2Cyli\temp\custom_cylinder.png'
   
    start_time = time.perf_counter()
    project_image_to_cylinder_optimized(input_image, output_image, 
                                      azimuth=180, elevation=20, height=3.5, radius=1.45)
    elapsed = time.perf_counter() - start_time
    print(f"耗时: {elapsed:.3f}s")