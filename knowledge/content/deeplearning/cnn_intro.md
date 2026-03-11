# 卷积神经网络(CNN)

CNN通过卷积操作提取局部特征，特别适合图像处理任务。卷积层、池化层、全连接层组成典型CNN架构。

## 核心要点

- 卷积操作：滑动窗口提取局部特征
- 卷积核(filter)：可学习的特征检测器
- 池化层：降维，增加平移不变性
- 经典架构：LeNet, AlexNet, VGG, ResNet

## 重要公式

$$
(f * g)(i,j) = \sum_m \sum_n f(m,n) \cdot g(i-m, j-n)
$$

- 2D卷积公式

$$
\text{output\_size} = \frac{\text{input\_size} - \text{kernel\_size} + 2 \times \text{padding}}{\text{stride}} + 1
$$

- 卷积输出尺寸计算

## 代码片段

```python
import torch.nn as nn

class SimpleCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
        self.fc = nn.Linear(64 * 7 * 7, 10)
    
    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))  # 28→14
        x = self.pool(F.relu(self.conv2(x)))  # 14→7
        x = x.view(-1, 64 * 7 * 7)
        return self.fc(x)
```

- 简单CNN：两层卷积+池化，最后全连接输出分类
