# 损失函数详解

损失函数衡量模型预测与真实值的差距，是训练神经网络的目标函数。不同任务需要选择合适的损失函数。

## 核心要点

- MSE(均方误差)：回归任务常用
- CrossEntropy(交叉熵)：分类任务常用
- BCELoss：二分类任务
- 损失函数的选择影响模型的优化方向

## 重要公式

$$
\text{MSE} = \frac{1}{n}\sum_{i=1}^{n}(y_i - \hat{y}_i)^2
$$

- 均方误差

$$
\text{CE} = -\sum_{i} y_i \log(\hat{y}_i)
$$

- 交叉熵损失

## 代码片段

```python
import torch.nn as nn

# 分类任务
criterion = nn.CrossEntropyLoss()
loss = criterion(logits, labels)  # logits: 未经softmax的输出

# 回归任务
criterion = nn.MSELoss()
loss = criterion(predictions, targets)
```

- PyTorch中常用损失函数的使用方式
