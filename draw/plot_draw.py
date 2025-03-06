import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors

# 打开Shapefile文件
shp_file_path = r'e:\work\sv_gonhoo\value_shp\0-Zvalue-Totle-fukuoka-city.shp'  # 替换为你的Shapefile路径
gdf = gpd.read_file(shp_file_path)

# 假设Shapefile中有一个名为 'Green_Visu' 的列包含我们需要的数据
column_name = 'Green Visu'  # 替换为实际列名

# 检查该列是否存在
if column_name not in gdf.columns:
    raise ValueError(f"列 '{column_name}' 不存在于Shapefile中。")

# 获取数据的最小值和最大值
min_value = gdf[column_name].min()
max_value = gdf[column_name].max()

# 将数据分为10个等级
num_classes = 10
bins = np.linspace(min_value, max_value, num_classes + 1)
gdf['class'] = np.digitize(gdf[column_name], bins)

# 创建颜色映射
cmap = plt.cm.get_cmap('viridis', num_classes)
colors = [cmap(i) for i in range(num_classes)]

# 绘制地图
fig, ax = plt.subplots(figsize=(10, 10))
gdf.plot(column='class', categorical=True, k=num_classes, cmap=cmap, linewidth=0.1, ax=ax,
         edgecolor='0.8', legend=True, legend_kwds={'title': column_name})

# 设置标题
plt.title(f'{column_name} ')

# 隐藏坐标轴
ax.set_axis_off()

# 保存为PNG文件
# output_file_path = 'output_image.png'  # 替换为你想要保存的文件路径
# plt.savefig(output_file_path, dpi=300, bbox_inches='tight', pad_inches=0)

# 显示图像
plt.show()