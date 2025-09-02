import os
from matplotlib.font_manager import FontProperties
import itertools
import matplotlib.pyplot as plt
import numpy as np
import numpy as np
from sklearn.metrics import confusion_matrix
import random
import numpy as np

def plot_confusion_matrix(cm, classes, normalize=False, title='Confusion matrix', cmap=plt.cm.Blues, save_path=None):
    """
    - cm : 计算出的混淆矩阵的值
    - classes : 混淆矩阵中每一行每一列对应的列
    - normalize : True:显示百分比, False:显示个数
    - save_path : 图片保存路径，如果为None则不保存
    """
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("显示百分比：")
        np.set_printoptions(formatter={'float': '{: 0.2f}'.format})
        print(cm)
    else:
        print('显示具体数字：')
        print(cm)
    
    # 设置支持中文的字体
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(cm, interpolation='nearest', cmap=cmap)
    
    # 添加颜色条并设置位置
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    
    # 设置标题和标签
    ax.set_title(title, pad=20)
    ax.set_xlabel('Predicted label', labelpad=10)
    ax.set_ylabel('True label', labelpad=10)
    
    # 设置刻度
    tick_marks = np.arange(len(classes))
    ax.set_xticks(tick_marks)
    ax.set_yticks(tick_marks)
    ax.set_xticklabels(classes, rotation=45, ha="right")
    ax.set_yticklabels(classes)
    
    # 调整坐标轴范围
    ax.set_ylim(len(classes)-0.5, -0.5)
    
    # 添加文本标签
    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        ax.text(j, i, format(cm[i, j], fmt),
                horizontalalignment="center",
                verticalalignment="center",
                color="white" if cm[i, j] > thresh else "black")
    
    # 调整布局
    fig.tight_layout()
    
    # 保存图片
    if save_path is not None:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图片已保存到: {save_path}")
    
    plt.show()

# 计算各类别的精确率、召回率和F1值
def calculate_metrics(conf_matrix):
    true_positives = np.diag(conf_matrix)
    false_positives = conf_matrix.sum(axis=0) - true_positives
    false_negatives = conf_matrix.sum(axis=1) - true_positives

    precision = true_positives / (true_positives + false_positives)
    recall = true_positives / (true_positives + false_negatives)
    f1_scores = 2 * (precision * recall) / (precision + recall)

    accuracy = np.trace(conf_matrix) / conf_matrix.sum()

    return accuracy, precision, recall, f1_scores


# 计算准确率
def calculate_accuracy(conf_matrix):
    true_positives = np.diag(conf_matrix)
    total_elements = conf_matrix.sum()
    accuracy = true_positives.sum() / total_elements
    return accuracy

# 计算精确率和召回率
def calculate_precision_recall(conf_matrix):
    precision = np.diag(conf_matrix) / conf_matrix.sum(axis=0)
    recall = np.diag(conf_matrix) / conf_matrix.sum(axis=1)
    return precision, recall

# 计算F1分数
def calculate_f1_score(precision, recall):
    f1_scores = 2 * (precision * recall) / (precision + recall)
    return f1_scores

if __name__ == '__main__':

    attack_types = ['宗教建筑','政府建筑','民居建筑','娱乐建筑','文教建筑','军事建筑',]
    # true_labels = [0, 0]  # 实际类别标签
    # predicted_labels = [0, 0]  # 预测类别标签
    # 计算混淆矩阵
    # cnf_matrix = confusion_matrix(true_labels, predicted_labels)

    # cnf_matrix = np.array([[81	,1	,3	,7	,3	,5],
    #                     [5	,32	,17	,22	,21	,3],
    #                     [2	,3	,57	,13	,18	,7],
    #                     [3	,24	,1	,49	,11	,12],
    #                     [11	,5	,13	,21	,35	,15],
    #                     [18	,26	,21	,3	,5	,27]])
    # plot_confusion_matrix(cnf_matrix, classes=attack_types, normalize=True, title='Confusion matrix',save_path=r'ConvNeXt-L_confusion_matrix_normalized.png')
    
    # cnf_matrix = np.array([[78	,2	,3	,7	,3	,7],
    #                     [5	,31	,18	,22	,21	,3],
    #                     [2	,3	,56	,15	,18	,7],
    #                     [3	,24	,1	,45	,15	,12],
    #                     [11	,5	,13	,21	,35	,15],
    #                     [18	,26	,20	,3	,5	,28]])
    # plot_confusion_matrix(cnf_matrix, classes=attack_types, normalize=True, title='Confusion matrix',save_path=r'Swin-B_confusion_matrix_normalized.png')
    
    # cnf_matrix = np.array([[75	,2	,3	,7	,6	,7],
    #                     [5	,33	,18	,20	,20	,4],
    #                     [2	,3	,58	,15	,20	,7],
    #                     [3	,23	,1	,46	,15	,12],
    #                     [11	,5	,13	,18	,38	,15],
    #                     [18	,26	,21	,3	,6	,26]])
    # plot_confusion_matrix(cnf_matrix, classes=attack_types, normalize=True, title='Confusion matrix',save_path=r'EfficientNet-B7_confusion_matrix_normalized.png')
    
    # cnf_matrix = np.array([[73	,5	,5	,7	,3	,7],
    #                     [5	,32	,18	,22	,21	,4],
    #                     [2	,3	,58	,12	,18	,7],
    #                     [3	,24	,1	,44	,16	,12],
    #                     [11	,5	,13	,20	,36	,15],
    #                     [18	,26	,21	,3	,3	,29]])
    # plot_confusion_matrix(cnf_matrix, classes=attack_types, normalize=True, title='Confusion matrix',save_path=r'ViT-B16_confusion_matrix_normalized.png')
    
    # cnf_matrix = np.array([[71	,5	,3	,10	,4	,7],
    #                     [8	,28	,18	,22	,21	,3],
    #                     [2	,3	,58	,15	,18	,5],
    #                     [3	,24	,1	,44	,16	,12],
    #                     [11	,5	,13	,21	,33	,17],
    #                     [18	,26	,19	,3	,5	,30]])
    # plot_confusion_matrix(cnf_matrix, classes=attack_types, normalize=True, title='Confusion matrix',save_path=r'RegNet-Y-16GF_confusion_matrix_normalized.png')
    
    cnf_matrix = np.array([[70	,5	,4	,10	,4	,7],
                        [5	,30	,19	,22	,21	,3],
                        [2	,3	,55	,16	,18	,7],
                        [3	,24	,1	,40	,20	,12],
                        [11	,5	,13	,21	,33	,17],
                        [18	,26	,21	,5	,5	,25]])
    plot_confusion_matrix(cnf_matrix, classes=attack_types, normalize=True, title='Confusion matrix',save_path=r'ResNet50_confusion_matrix_normalized.png')

    # 归一化
    # 不归一化
    # plot_confusion_matrix(cnf_matrix, classes=attack_types, normalize=True, title='Confusion matrix')


    # 计算指标
    accuracy = calculate_accuracy(cnf_matrix)
    precision, recall = calculate_precision_recall(cnf_matrix)
    f1_scores = calculate_f1_score(precision, recall)

    # 打印结果
    print(f"Accuracy: {accuracy}")
    print(f"Precision: {precision}")
    print(f"Recall: {recall}")
    print(f"F1 Scores: {f1_scores}")
