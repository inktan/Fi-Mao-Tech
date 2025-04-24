import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. 设置全局样式（提升美观度）
sns.set_style("whitegrid")  # 白色背景+网格线
plt.rcParams['font.family'] = 'Arial'  # 设置字体
plt.rcParams['axes.edgecolor'] = '#333333'  # 坐标轴颜色

# 2. 定义配色方案（直接、间接、总和的颜色）
palette = {
    'Direct': '#4C72B0',  # 深蓝色
    'Indirect': '#DD8452',  # 橙红色
    'Total': '#55A868'  # 绿色（可选，堆叠图通常不显示总和）
}

# 3. 读取文件夹中的所有CSV文件
folder_path = r"E:\work\sv_juanjuanmao\20250308\八条路线\plot"
output_folder = os.path.join(folder_path, "plots")  # 输出子文件夹
os.makedirs(output_folder, exist_ok=True)  # 自动创建输出文件夹

csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
target_vars = ['ashcan', 'poster', 'green', 'sky', 'window', 
               'chair', 'OpenSocial', 'shop', 'h_value', 'traffic']

# 4. 为每个文件生成图表
for file in csv_files:
    file_path = os.path.join(folder_path, file)
    df = pd.read_csv(file_path)  # 读取CSV
    
    # 筛选目标变量（如果CSV中已筛选过可跳过）
    df = df[df['Variable'].isin(target_vars)]
    
    # 创建画布
    plt.figure(figsize=(12, 6), dpi=300)  # 高分辨率
    
    # 绘制堆叠柱状图（仅Direct和Indirect）
    ax = df[['Direct', 'Indirect']].plot(
        kind='bar',
        stacked=True,
        color=[palette['Direct'], palette['Indirect']],
        width=0.7,
        edgecolor='white',  # 柱状边框色
        linewidth=0.5
    )
    
    # 添加Total的虚线参考线（可选）
    ax.plot(range(len(df)), df['Total'], 
            '--o', color=palette['Total'], 
            markersize=5, label='Total')
    
    # 设置标题和标签
    title = file.replace('.csv', '').replace('_', ' ')
    ax.set_title(f'{title}\nDirect vs Indirect Contributions', 
                 fontsize=14, pad=20)
    ax.set_xlabel('Variable', fontsize=12)
    ax.set_ylabel('Value', fontsize=12)
    
    # 调整X轴标签
    ax.set_xticks(range(len(df)))
    ax.set_xticklabels(df['Variable'], rotation=45, ha='right')
    
    # 添加图例和网格
    ax.legend(frameon=True, facecolor='white')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # 移除多余的边框
    sns.despine(left=True, bottom=True)
    
    # 自动调整布局并保存
    plt.tight_layout()
    output_path = os.path.join(output_folder, f"{title}.png")
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()  # 关闭当前图形，避免内存泄漏

print(f"所有图表已保存至：{output_folder}")