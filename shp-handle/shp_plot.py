import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as cx
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import matplotlib.patheffects as path_effects

# 1. 读取点数据Shapefile
point_shp = r'e:\work\sv_jumaorizhi\xc_src_complexity_harmony_averaged.shp'  # 替换为你的点数据路径
output_png = r'e:\work\sv_jumaorizhi\xc_src_complexity_harmony_averaged.png'  # 输出图片路径

gdf = gpd.read_file(point_shp)

# 2. 检查必要字段
if 'complexity' not in gdf.columns:
    raise ValueError("点数据中缺少'complexity'字段")

# 3. 创建图形和坐标轴
fig, ax = plt.subplots(figsize=(12, 12), dpi=300)

# 4. 设置颜色映射
cmap = plt.get_cmap('viridis')  # 使用viridis色阶
norm = Normalize(vmin=gdf['complexity'].min(), vmax=gdf['complexity'].max())

# 5. 绘制点数据（按complexity值着色）
scatter = gdf.plot(
    ax=ax,
    column='complexity',
    cmap=cmap,
    markersize=50,  # 点大小
    alpha=0.8,      # 透明度
    edgecolor='white',  # 点边缘颜色
    linewidth=0.5,  # 点边缘宽度
    legend=False    # 稍后手动添加图例
)

# 6. 添加底图
# cx.add_basemap(
#     ax,
#     crs=gdf.crs.to_string(),
#     source=cx.providers.CartoDB.Positron,  # 使用CartoDB底图
    # zoom=14  # 调整缩放级别
# )

# 7. 添加指北针（右上角）
ax.annotate(
    'N',
    xy=(0.95, 0.95),
    xycoords='axes fraction',
    fontsize=20,
    ha='center',
    va='center',
    bbox=dict(boxstyle='circle,pad=0.3', fc='white', ec='black', lw=1)
)
# 添加指北针箭头
ax.annotate(
    '',
    xy=(0.95, 0.90),
    xycoords='axes fraction',
    xytext=(0.95, 0.95),
    arrowprops=dict(arrowstyle='->', lw=2, color='black')
)

# 8. 添加色阶图例（右下角）
cax = inset_axes(
    ax,
    width='3%',
    height='30%',
    loc='lower right',
    bbox_to_anchor=(0.15, 0.05, 1, 1),
    bbox_transform=ax.transAxes
)
sm = ScalarMappable(norm=norm, cmap=cmap)
sm.set_array([])
cbar = fig.colorbar(sm, cax=cax, orientation='vertical')
cbar.set_label('Complexity', fontsize=10)

# 9. 添加比例尺（最底右下角）
def add_scale_bar(ax, length_meters, location=(0.85, 0.05)):
    # 将米转换为地图单位（Web墨卡托）
    length = length_meters / 1.0  # Web墨卡托单位已经是米
    
    # 绘制比例尺线
    ax.plot(
        [location[0], location[0] + length/ax.get_xlim()[1]],
        [location[1], location[1]],
        color='black',
        linewidth=2,
        transform=ax.transAxes,
        path_effects=[path_effects.withStroke(linewidth=3, foreground="white")]
    )
    
    # 添加标注
    ax.text(
        location[0] + (length/ax.get_xlim()[1])/2,
        location[1] + 0.01,
        f"{length_meters} m",
        ha='center',
        va='bottom',
        transform=ax.transAxes,
        fontsize=10,
        bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1)
    )

add_scale_bar(ax, 500)  # 添加500米比例尺

# 10. 调整图形并保存
plt.tight_layout()
plt.savefig(output_png, dpi=300, bbox_inches='tight', pad_inches=0.1)
print(f"地图已保存至: {output_png}")

# 可选：显示图形
# plt.show()