# 正则化技术

正则化技术用于防止模型过拟合，提高泛化能力。Dropout、权重衰减、数据增强是常用方法。

## 核心要点

- Dropout：训练时随机丢弃神经元，测试时关闭
- Batch Normalization：标准化层输入，加速训练
- 权重衰减(L2正则化)：限制权重大小
- 数据增强：扩充训练数据多样性

## 重要公式

$$
\text{Dropout}(x) = \frac{x \cdot m}{1-p}, \quad m \sim \text{Bernoulli}(1-p)
$$

- Dropout公式，m是掩码

$$
\hat{x} = \frac{x - \mu}{\sqrt{\sigma^2 + \epsilon}}
$$

- Batch Normalization标准化

## 代码片段

```python
import torch.nn as nn

class RegularizedNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(784, 256)
        self.bn1 = nn.BatchNorm1d(256)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(256, 10)
    
    def forward(self, x):
        x = F.relu(self.bn1(self.fc1(x)))
        x = self.dropout(x)
        return self.fc2(x)
```

- 结合BatchNorm和Dropout的网络
