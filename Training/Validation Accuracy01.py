import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from scipy.interpolate import make_interp_spline

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
    'ResNet50': simulate_model_training(0.70, epochs),
    'RegNet-Y-16GF': simulate_model_training(0.71, epochs),
    'ViT-B/16': simulate_model_training(0.73, epochs),
    'EfficientNet-B7': simulate_model_training(0.75, epochs),
    'Swin-B': simulate_model_training(0.78, epochs),
    'ConvNeXt-L': simulate_model_training(0.82, epochs)
}

plt.figure(figsize=(24, 14), dpi=200)

linestyles = [':', '-.', '--', '-', (0, (3, 1, 1, 1)), (0, (5, 5))]  # 最后两种是自定义虚线模式

linewidth = 2.5
marker_size = 18

markers = ['o', 's', 'D', '^', 'v', 'p']  # 圆形、方形、菱形、上三角、下三角、五边形
for i, (model_name, (x, train_acc, val_acc)) in enumerate(models.items()):
    # 训练和验证曲线（降低验证曲线透明度）
    plt.plot(x, train_acc, 
             label=f'{model_name} (Train)',
             color='black', 
             linestyle=linestyles[i],
             linewidth=linewidth,
             alpha=0.8)
    plt.plot(x, val_acc, 
             color='gray', 
             linestyle=linestyles[i],
             linewidth=linewidth,
             alpha=0.4)  # 透明度降低
    
    # 标记最佳验证点（调整大小和颜色）
    best_val_idx = np.argmax(val_acc)
    best_val_acc = val_acc[best_val_idx]
    best_epoch = x[best_val_idx]
    plt.scatter(best_epoch, best_val_acc, 
                color='red',  # 高对比度颜色
                marker=markers[i],
                s=150,       # 适当大小
                edgecolors='white',
                linewidths=1.5,
                zorder=5,    # 确保在最上层
                label=f'{model_name} Best Val: {best_val_acc:.2%}')
    
    # 垂直线（可选）
    plt.axvline(x=best_epoch, ymin=0, ymax=(best_val_acc-0.6)/0.25, 
                color='black', 
                linestyle=':', 
                linewidth=1.5,
                alpha=0.3)  # 降低透明度

plt.xlabel('Training Epochs', fontsize=24)  # 坐标轴标签放大
plt.ylabel('Accuracy', fontsize=24)

plt.xlim(1, epochs)
plt.ylim(0.6, 0.85)
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
plt.gca().yaxis.set_major_formatter('{x:.0%}')

plt.xticks(fontsize=20)
plt.yticks(fontsize=20)

plt.grid(True, linestyle=':', alpha=0.5, linewidth=1.2)

plt.legend(loc='lower right', fontsize=20, framealpha=0.9,
           handlelength=3,  # 图例句柄加长
           markerscale=1.5) # 图例标记放大

plt.tight_layout()
plt.savefig("train_accuracy_comparison_500.png", bbox_inches='tight', dpi=200)