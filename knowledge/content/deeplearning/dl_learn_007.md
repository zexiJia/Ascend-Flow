# 优化器原理与选择

优化器决定了如何根据梯度更新模型参数。不同优化器有不同的收敛特性和适用场景。

## 核心要点

- SGD：最基本的梯度下降，可加动量加速收敛
- Adam：结合动量和自适应学习率，最常用
- 学习率调度：随训练进行调整学习率
- 权重衰减(L2正则化)：防止过拟合

## 重要公式

$$
v_t = \beta v_{t-1} + (1-\beta)\nabla L
$$

- 动量更新公式

$$
w_t = w_{t-1} - \eta \cdot \frac{m_t}{\sqrt{v_t} + \epsilon}
$$

- Adam更新公式(简化)

## 代码片段

```python
import torch.optim as optim

# Adam优化器
optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-4)

# 学习率调度
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.1)

for epoch in range(epochs):
    train(...)
    scheduler.step()  # 每10个epoch学习率×0.1
```

- Adam优化器配合学习率调度的使用
