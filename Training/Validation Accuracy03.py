import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from scipy.interpolate import make_interp_spline

# 设置科研风格的配色方案 - 使用ColorBrewer的定性配色方案
plt.style.use('default')  # 重置为默认样式
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']  # Tableau10配色

np.random.seed(42)

def simulate_model_training(base_acc, num_epochs=300):
    # 模拟训练准确率
    train_acc = np.zeros(num_epochs)
    for epoch in range(num_epochs):
        if epoch < 50:
            train_acc[epoch] = 0.1 + (base_acc-0.1) * (1 - np.exp(-epoch/15))
        else:
            train_acc[epoch] = base_acc * 0.95 + (base_acc * 0.05) * (1 - np.exp(-(epoch-80)/100)) + np.random.normal(0, 0.003)
    train_acc = np.clip(train_acc, 0, base_acc)
    
    val_acc = train_acc - np.random.uniform(0.02, 0.1, size=num_epochs) * (1 - train_acc)
    val_acc = np.clip(val_acc + np.random.normal(0, 0.002, size=num_epochs), 0, 1)
    
    x = np.arange(num_epochs)
    x_new = np.linspace(0, num_epochs-1, num_epochs*3)
    
    spl_train = make_interp_spline(x, train_acc, k=3)
    train_acc_smooth = spl_train(x_new)
    
    spl_val = make_interp_spline(x, val_acc, k=3)
    val_acc_smooth = spl_val(x_new)
    
    return x_new+1, train_acc_smooth, val_acc_smooth

epochs = 500
models = {
    'ResNet50': simulate_model_training(0.581, epochs),
    'RegNet-Y-16GF': simulate_model_training(0.593, epochs),
    'ViT-B/16': simulate_model_training(0.61, epochs),
    'EfficientNet-B7': simulate_model_training(0.63, epochs),
    'Swin-B': simulate_model_training(0.65, epochs),
    'ConvNeXt-L': simulate_model_training(0.697, epochs)
}

# 创建图形
plt.figure(figsize=(20, 12), dpi=300)  # 调整尺寸以适应彩色图例
ax = plt.gca()

# 为训练和验证曲线使用不同的线型
train_linestyle = '-'
val_linestyle = '--'

for i, (model_name, (x, train_acc, val_acc)) in enumerate(models.items()):
    color = colors[i % len(colors)]
    
    # 训练曲线 - 实线
    plt.plot(x, train_acc, 
             label=f'{model_name} (Train)',
             color=color, 
             linestyle=train_linestyle,
             linewidth=2,
             alpha=0.9)
    
    # 验证曲线 - 虚线，稍微淡一些
    plt.plot(x, val_acc, 
             label=f'{model_name} (Val)',
             color='gray', 
             linestyle=val_linestyle,
             linewidth=1,
             alpha=0.8)
    
    # 标记最佳验证点
    best_val_idx = np.argmax(val_acc)
    best_val_acc = val_acc[best_val_idx]
    best_epoch = x[best_val_idx]
    
    plt.scatter(best_epoch, best_val_acc, 
                # color=color,
                color='black',
                marker='o',
                s=150,
                edgecolors='white',
                linewidths=2.0,
                zorder=5,
                label=f'{model_name} Best: {best_val_acc:.1%}')

# 设置坐标轴和标签
# plt.xlabel('Training Epochs', fontsize=20, fontweight='bold')
# plt.ylabel('Accuracy', fontsize=20, fontweight='bold')
plt.xlabel('Training Epochs', fontsize=30 )
plt.ylabel('Accuracy', fontsize=30)

plt.xlim(1, epochs)
plt.ylim(0.35, 0.75)
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0%}'))

# 设置刻度字体
plt.xticks(fontsize=25)
plt.yticks(fontsize=25)

# 添加网格
plt.grid(True, linestyle=':', alpha=0.7, linewidth=1.0)

# 设置图例 - 分两列显示以避免重叠
legend_elements = []
for i, model_name in enumerate(models.keys()):
    color = colors[i % len(colors)]
    legend_elements.extend([
        plt.Line2D([0], [0], color=color, linestyle=train_linestyle, linewidth=0.151,
                  label=f'{model_name} Train'),
        plt.Line2D([0], [0], color='gray', linestyle=val_linestyle, linewidth=0.151,
                  label=f'{model_name} Val'),
        plt.Line2D([0], [0], color='black', marker='o', linestyle='None', markersize=10,
                  markerfacecolor='black', markeredgecolor='white', markeredgewidth=1.5,
                  label=f'{model_name} Best')
    ])

# 创建图例
legend = plt.legend(handles=legend_elements, loc='lower right', 
                   ncol=2, framealpha=0.6795, handlelength=2.5,
                   fontsize=20,  # 图例文字大小设置为25
                   bbox_to_anchor=(0.99, 0.01))  # 微调位置

# 调整图例句柄的大小
for handle in legend.legend_handles:
    if hasattr(handle, 'get_markersize'):
        handle.set_markersize(12)  # 增大图例中标记点的大小
    if hasattr(handle, 'get_linewidth'):
        handle.set_linewidth(4)    # 增大图例中线的粗细

# 添加边框
for spine in ax.spines.values():
    spine.set_linewidth(1.5)

plt.tight_layout()
plt.savefig("train_accuracy_comparison_500_color.png", 
            bbox_inches='tight', 
            dpi=300,
            facecolor='white',  # 确保背景为白色
            edgecolor='none')

# plt.show()