# 神经网络基础

神经网络是深度学习的基础。理解神经元、层、激活函数等概念是学习深度学习的第一步。

## 核心要点

- 神经元：接收输入，加权求和，经激活函数输出
- 前向传播：输入层 → 隐藏层 → 输出层
- 激活函数：引入非线性，如ReLU, Sigmoid, Tanh
- 全连接层：每个神经元与上一层所有神经元相连

## 重要公式

$$
y = \sigma(\sum_{i} w_i x_i + b)
$$

- 神经元的计算：加权求和后经激活函数

$$
\text{ReLU}(x) = \max(0, x)
$$

- ReLU激活函数

## 代码片段

```python
import torch.nn as nn

class SimpleNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(784, 128)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(128, 10)
    
    def forward(self, x):
        x = self.relu(self.fc1(x))
        return self.fc2(x)
```

- PyTorch实现的简单神经网络：输入784维，隐藏层128个神经元，输出10类
