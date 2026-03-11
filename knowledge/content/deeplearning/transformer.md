# Transformer与注意力机制

Transformer抛弃了RNN的循环结构，完全基于注意力机制。它是GPT、BERT等大模型的基础架构。

## 核心要点

- 自注意力(Self-Attention)：计算序列中每个位置对其他位置的关注度
- 多头注意力：并行多个注意力头，捕获不同方面的依赖关系
- 位置编码：为无序的注意力机制添加位置信息
- Encoder-Decoder架构：编码器理解输入，解码器生成输出

## 重要公式

$$
\text{Attention}(Q,K,V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
$$

- 缩放点积注意力公式

$$
\text{MultiHead}(Q,K,V) = \text{Concat}(head_1, ..., head_h)W^O
$$

- 多头注意力

## 代码片段

```python
import torch
import torch.nn.functional as F

def scaled_dot_product_attention(Q, K, V, mask=None):
    d_k = Q.size(-1)
    scores = torch.matmul(Q, K.transpose(-2, -1)) / (d_k ** 0.5)
    if mask is not None:
        scores = scores.masked_fill(mask == 0, -1e9)
    attn = F.softmax(scores, dim=-1)
    return torch.matmul(attn, V)
```

- 缩放点积注意力的PyTorch实现
