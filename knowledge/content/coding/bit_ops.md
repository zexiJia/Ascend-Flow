# 位运算技巧

位运算直接操作二进制位，速度极快。掌握常见位运算技巧可以优雅地解决很多问题。

## 核心要点

- 基本运算：与(&)、或(|)、异或(^)、取反(~)、移位(<<, >>)
- n & (n-1)：消除最低位的1
- n & (-n)：获取最低位的1
- 异或性质：a^a=0, a^0=a

## 示例

```python
# Plus One 的位运算思路
def plusOne(digits):
    # 将数组转为整数，加1，再转回数组
    num = int(''.join(map(str, digits))) + 1
    return [int(d) for d in str(num)]
```

- 利用Python大整数特性，直接进行数值运算
