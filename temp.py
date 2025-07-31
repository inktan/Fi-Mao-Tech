import torch
import torch.nn.functional as F
from torchvision import models, transforms
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import cv2

# 加载预训练的ResNet50模型
model = models.resnet50(pretrained=True)
model.eval()  # 设置为评估模式

# 定义图像预处理
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# 加载并预处理图像
image_path = r'e:\work\sv_zhoujunling\澳门历史建筑装饰纹样-clip_kmeans_20\8\decorate_77.png'  # 替换为你的图片路径
image = Image.open(image_path)
input_tensor = preprocess(image)
input_batch = input_tensor.unsqueeze(0)  # 创建batch维度

# 注册hook来获取特征图和梯度
features = None
gradients = None

def feature_hook(module, input, output):
    global features
    features = output
    
def gradient_hook(module, grad_input, grad_output):
    global gradients
    gradients = grad_output[0]

# 获取最后一个卷积层
target_layer = model.layer4[-1].conv3
target_layer.register_forward_hook(feature_hook)
target_layer.register_backward_hook(gradient_hook)

# 前向传播
output = model(input_batch)

# 选择最高分的类别进行反向传播
predicted_class = output.argmax(dim=1)
model.zero_grad()
one_hot = torch.zeros_like(output)
one_hot[0][predicted_class] = 1
output.backward(gradient=one_hot)

# 计算Grad-CAM
pooled_gradients = torch.mean(gradients, dim=[0, 2, 3])
for i in range(features.size()[1]):
    features[:, i, :, :] *= pooled_gradients[i]
    
heatmap = torch.mean(features, dim=1).squeeze()
heatmap = F.relu(heatmap)  # 应用ReLU
heatmap /= torch.max(heatmap)  # 归一化

# 转换为numpy数组
heatmap = heatmap.detach().numpy()

# 调整热力图大小以匹配原始图像
img = cv2.imread(image_path)
heatmap = cv2.resize(heatmap, (img.shape[1], img.shape[0]))
heatmap = np.uint8(255 * heatmap)
heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

# 叠加热力图到原始图像
superimposed_img = heatmap * 0.4 + img * 0.6
superimposed_img = np.clip(superimposed_img, 0, 255).astype(np.uint8)

# 显示结果
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
plt.title('Original Image')
plt.axis('off')

plt.subplot(1, 2, 2)
plt.imshow(cv2.cvtColor(superimposed_img, cv2.COLOR_BGR2RGB))
plt.title('Grad-CAM Heatmap')
plt.axis('off')

plt.show()