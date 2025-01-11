import os
from matplotlib.font_manager import FontProperties
import itertools
import matplotlib.pyplot as plt
import numpy as np
import numpy as np
from sklearn.metrics import confusion_matrix
import random
import numpy as np

# 绘制混淆矩阵
def plot_confusion_matrix(cm, classes, normalize=False, title='Confusion matrix', cmap=plt.cm.Blues):
    """
    - cm : 计算出的混淆矩阵的值
    - classes : 混淆矩阵中每一行每一列对应的列
    - normalize : True:显示百分比, False:显示个数
    """
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("显示百分比：")
        np.set_printoptions(formatter={'float': '{: 0.2f}'.format})
        print(cm)
    else:
        print('显示具体数字：')
        print(cm)
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)
    # 指定支持中文的字体，这里以“SimHei”字体为例
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False  # 用于正常显示负号

    # matplotlib版本问题，如果不加下面这行代码，则绘制的混淆矩阵上下只能显示一半，有的版本的matplotlib不需要下面的代码，分别试一下即可
    plt.ylim(len(classes) - 0.5, -0.5)
    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")
    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
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

    cnf_matrix = np.array([[81	,1	,3	,7	,3	,5],
                        [5	,32	,17	,22	,21	,3],
                        [2	,3	,57	,13	,18	,7],
                        [3	,24	,1	,49	,11	,12],
                        [11	,5	,13	,21	,35	,15],
                        [18	,26	,21	,3	,5	,27]])


    # 归一化
    plot_confusion_matrix(cnf_matrix, classes=attack_types, normalize=True, title='Confusion matrix')
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
