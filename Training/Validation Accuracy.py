import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from scipy.interpolate import make_interp_spline

# 设置随机种子以保证可重复性
np.random.seed(42)

# 模拟单个模型的训练过程（返回训练和验证准确率）
def simulate_model_training(base_acc, num_epochs=300):
    # 模拟训练准确率
    train_acc = np.zeros(num_epochs)
    for epoch in range(num_epochs):
        if epoch < 50:
            train_acc[epoch] = 0.1 + (base_acc-0.1) * (1 - np.exp(-epoch/15))
        else:
            train_acc[epoch] = base_acc * 0.95 + (base_acc * 0.05) * (1 - np.exp(-(epoch-50)/100)) + np.random.normal(0, 0.003)
    train_acc = np.clip(train_acc, 0, base_acc)
    
    # 模拟验证准确率（通常比训练准确率低且更平滑）
    val_acc = train_acc - np.random.uniform(0.02, 0.1, size=num_epochs) * (1 - train_acc)
    val_acc = np.clip(val_acc + np.random.normal(0, 0.002, size=num_epochs), 0, 1)
    
    # 对训练和验证曲线进行平滑处理
    x = np.arange(num_epochs)
    x_new = np.linspace(0, num_epochs-1, num_epochs*3)
    
    # 训练曲线平滑
    spl_train = make_interp_spline(x, train_acc, k=3)
    train_acc_smooth = spl_train(x_new)
    
    # 验证曲线平滑
    spl_val = make_interp_spline(x, val_acc, k=3)
    val_acc_smooth = spl_val(x_new)
    
    return x_new+1, train_acc_smooth, val_acc_smooth

# 模拟四种模型的训练数据
epochs = 500
models = {
    'ConvNeXt-T': simulate_model_training(0.70, epochs),
    'ConvNeXt-S': simulate_model_training(0.75, epochs),
    'ConvNeXt-B': simulate_model_training(0.78, epochs),
    'ConvNeXt-L': simulate_model_training(0.82, epochs)
}

# 创建图像（大尺寸高分辨率）
plt.figure(figsize=(24, 14), dpi=200)

# 定义线型和标记样式（按比例放大）
linestyles = [':', '-.', '--', '-']
linewidth = 2.5  # 加粗线条以适应大图
marker_size = 18  # 放大标记点

# 绘制每种模型的训练和验证曲线
for i, (model_name, (x, train_acc, val_acc)) in enumerate(models.items()):
    # 绘制训练曲线（黑色）
    plt.plot(x, train_acc, 
             label=f'{model_name} (Train)',
             color='black', 
             linestyle=linestyles[i],
             linewidth=linewidth,
             alpha=0.8)
    
    # 绘制验证曲线（灰色）
    plt.plot(x, val_acc, 
             color='gray', 
             linestyle=linestyles[i],
             linewidth=linewidth,
             alpha=0.6)
    
    # 找到并标记最佳验证准确率
    best_val_idx = np.argmax(val_acc)
    best_val_acc = val_acc[best_val_idx]
    best_epoch = x[best_val_idx]
    
    # 使用不同形状的标记点
    markers = ['o', 's', 'D', '^']
    plt.scatter(best_epoch, best_val_acc, 
                color='black', 
                marker=markers[i],
                s=marker_size**2,  # 面积按比例放大
                edgecolors='white',
                linewidths=1.5,    # 边缘线加粗
                zorder=10,
                label=f'{model_name} Best Val: {best_val_acc:.2%}')
    
    # 添加虚线连接
    plt.axvline(x=best_epoch, ymin=0, ymax=(best_val_acc-0.6)/0.25, 
                color='black', 
                linestyle=':', 
                linewidth=1.5,     # 虚线加粗
                alpha=0.5)

# 添加标题和标签（放大字体）
plt.title('ConvNeXt Models Training/Validation Accuracy (500 Epochs)', 
          fontsize=28, pad=25)  # 标题字体放大
plt.xlabel('Training Epochs', fontsize=24)  # 坐标轴标签放大
plt.ylabel('Accuracy', fontsize=24)

# 设置坐标轴
plt.xlim(1, epochs)
plt.ylim(0.6, 0.85)
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
plt.gca().yaxis.set_major_formatter('{x:.0%}')

# 调整刻度标签大小
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)

# 添加网格（线条适当加粗）
plt.grid(True, linestyle=':', alpha=0.5, linewidth=1.2)

# 添加图例（放大并优化位置）
plt.legend(loc='lower right', fontsize=20, framealpha=0.9,
           handlelength=3,  # 图例句柄加长
           markerscale=1.5) # 图例标记放大

# 添加模型性能排序说明（放大字体）
plt.text(10, 0.615, 'Model Size: T < S < B < L', fontsize=22, 
         bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=10))

# 调整布局并显示图像
plt.tight_layout()
plt.savefig("train_accuracy_comparison_500.png", bbox_inches='tight', dpi=200)