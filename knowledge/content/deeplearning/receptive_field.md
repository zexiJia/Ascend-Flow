# 感受野(Receptive Field)

感受野是CNN中的核心概念，指的是神经网络中某一层的输出特征图上的一个像素点，对应到输入图像上的区域大小。理解感受野对于设计网络架构至关重要。

## 核心要点

- 定义：输出特征图上一个点「看到」的输入区域大小
- 局部感受野：卷积核大小决定的直接感受范围
- 有效感受野：随着网络加深，感受野不断扩大
- 计算公式：RF_out = RF_in + (kernel_size - 1) × stride_product
- 感受野与网络深度：深层特征有更大感受野，捕获更全局的信息
- 空洞卷积：不增加参数量的情况下扩大感受野

## 重要公式

$$
RF_n = RF_{n-1} + (k_n - 1) \times \prod_{i=1}^{n-1} s_i
$$

- 感受野递推公式：k是卷积核大小，s是步长

$$
RF = 1 + \sum_{i=1}^{n}(k_i - 1) \times \prod_{j=1}^{i-1} s_j
$$

- 感受野通用计算公式

$$
RF_{dilated} = k + (k-1) \times (d-1)
$$

- 空洞卷积的等效卷积核大小，d是膨胀率

## 代码片段

```python
# 计算感受野
def calculate_receptive_field(layers):
    '''
    layers: [(kernel_size, stride), ...]
    '''
    rf = 1
    stride_product = 1
    for k, s in layers:
        rf = rf + (k - 1) * stride_product
        stride_product *= s
    return rf

# VGG-16 前几层感受野
layers = [(3,1), (3,1), (2,2), (3,1), (3,1), (2,2)]
print(calculate_receptive_field(layers))  # 输出: 16
```

- 感受野计算：遍历每层累加 (k-1) × 之前所有层stride的乘积

```python
import torch.nn as nn

# 使用空洞卷积扩大感受野
class DilatedConvBlock(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        # 普通3x3卷积，感受野=3
        self.conv1 = nn.Conv2d(in_ch, out_ch, 3, padding=1)
        # 空洞卷积，dilation=2，等效感受野=5
        self.conv2 = nn.Conv2d(out_ch, out_ch, 3, padding=2, dilation=2)
        # 空洞卷积，dilation=4，等效感受野=9
        self.conv3 = nn.Conv2d(out_ch, out_ch, 3, padding=4, dilation=4)
    
    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        return x  # 最终感受野很大但参数量不变
```

- 空洞卷积(Dilated/Atrous Conv)：用于语义分割，不增加参数扩大感受野

```python
# 感受野可视化思路
import torch
import torch.nn.functional as F

def visualize_rf(model, input_size=224):
    '''
    通过梯度反向传播可视化有效感受野
    '''
    x = torch.zeros(1, 3, input_size, input_size, requires_grad=True)
    y = model(x)
    
    # 选择中心点
    center = y.shape[-1] // 2
    y[0, 0, center, center].backward()
    
    # 梯度的绝对值表示输入对该输出点的贡献
    rf_map = x.grad.abs().sum(dim=1)[0]
    return rf_map  # 可视化这个图看感受野形状
```

- 有效感受野可视化：中心区域贡献大，边缘衰减（高斯分布形状）
