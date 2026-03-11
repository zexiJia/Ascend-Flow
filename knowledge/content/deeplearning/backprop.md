# 反向传播算法

反向传播是训练神经网络的核心算法。通过链式法则计算梯度，然后用梯度下降更新参数。

## 核心要点

- 损失函数：衡量预测与真实值的差距
- 链式法则：复合函数求导，从输出层反向传播
- 梯度下降：w = w - lr × ∂L/∂w
- 自动微分：PyTorch的autograd自动计算梯度

## 重要公式

$$
\frac{\partial L}{\partial w} = \frac{\partial L}{\partial y} \cdot \frac{\partial y}{\partial w}
$$

- 链式法则求梯度

$$
w_{new} = w_{old} - \eta \cdot \nabla_w L
$$

- 梯度下降更新参数

## 代码片段

```python
# PyTorch自动反向传播
optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

for epoch in range(epochs):
    output = model(input)
    loss = criterion(output, target)
    
    optimizer.zero_grad()  # 清零梯度
    loss.backward()        # 反向传播
    optimizer.step()       # 更新参数
```

- PyTorch训练循环：前向传播、计算损失、反向传播、更新参数
