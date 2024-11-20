import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import imageio

# 读取图片
# 这里我们使用一个内置的示例图片
img = imageio.imread(r'c:\Users\wang.tan.GOA\Pictures\qwe.png')

# 提取RGB值
# 假设图片是RGB格式
r, g, b = img[:,:,0], img[:,:,1], img[:,:,2]

# 将三维数组展平为一维数组
r = r.flatten()
g = g.flatten()
b = b.flatten()

# 创建3D散点图
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
ax.scatter(r, g, b)

# 设置坐标轴标签
ax.set_xlabel('Red')
ax.set_ylabel('Green')
ax.set_zlabel('Blue')

# 显示图表
plt.show()
