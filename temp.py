import cv2
import numpy as np

def create_cylindrical_projection(image_path, output_size=(800, 400), f=300):
    """
    创建圆柱投影的2D图像
    
    参数:
        image_path: 输入全景图路径
        output_size: 输出图像尺寸 (宽, 高)
        f: 虚拟焦距，控制变形程度
    """
    # 读取图像
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("无法读取图像")
    
    h, w = img.shape[:2]
    out_w, out_h = output_size
    
    # 创建输出图像
    result = np.zeros((out_h, out_w, 3), dtype=np.uint8)
    
    # 中心点
    cx = w / 2
    cy = h / 2
    
    # 生成输出图像的坐标
    for y_out in range(out_h):
        for x_out in range(out_w):
            # 归一化坐标
            x_norm = (x_out - out_w/2) / f
            y_norm = (y_out - out_h/2) / f
            
            # 计算对应的全景图坐标
            theta = np.arctan(x_norm)
            x_img = cx + (theta / np.pi) * cx
            y_img = cy + y_norm * f
            
            # 边界检查
            if 0 <= x_img < w and 0 <= y_img < h:
                result[y_out, x_out] = img[int(y_img), int(x_img)]
    
    return result

# 使用示例
cylindrical_img = create_cylindrical_projection(r"e:\work\sv_huang_g\test\results\10512.jpg")
cv2.imshow("Cylindrical Projection", cylindrical_img)
cv2.waitKey(0)
cv2.destroyAllWindows()
# 使用示例
# if __name__ == "__main__":
#     # 读取输入图像
#     input_img = cv2.imread(r"e:\work\sv_huang_g\test\results\10512.jpg")
    
#     if input_img is not None:
#         # 转换为等距圆柱投影
#         equirect_img = panorama_to_equirectangular(input_img)
        
#         # 保存结果
#         cv2.imwrite(r'e:\work\sv_huang_g\test\results\10512_cylin_02.png', equirect_img)
#         print("等距圆柱投影图像已保存为 equirectangular_output.jpg")
#     else:
#         print("无法读取输入图像")
