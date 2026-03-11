# 循环神经网络(RNN)

RNN通过循环结构处理序列数据，能够记住历史信息。LSTM和GRU解决了原始RNN的梯度消失问题。

## 核心要点

- 隐藏状态：h_t = f(h_{t-1}, x_t)，记录历史信息
- LSTM：引入门控机制，包括遗忘门、输入门、输出门
- GRU：简化版LSTM，只有重置门和更新门
- 双向RNN：同时考虑前后文信息

## 重要公式

$$
h_t = \tanh(W_{hh} h_{t-1} + W_{xh} x_t + b)
$$

- RNN隐藏状态更新公式

$$
f_t = \sigma(W_f \cdot [h_{t-1}, x_t] + b_f)
$$

- LSTM遗忘门

## 代码片段

```python
import torch.nn as nn

class TextClassifier(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, num_classes):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, num_classes)
    
    def forward(self, x):
        x = self.embedding(x)
        _, (h_n, _) = self.lstm(x)
        return self.fc(h_n.squeeze(0))
```

- LSTM文本分类：词嵌入→LSTM→取最后隐藏状态→分类
