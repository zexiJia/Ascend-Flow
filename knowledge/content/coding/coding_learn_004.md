# 动态规划入门：最大子数组和

动态规划(DP)是解决最优化问题的重要方法。核心思想是将大问题分解为子问题，通过状态转移方程递推求解。

## 核心要点

- DP三要素：状态定义、转移方程、初始条件
- 状态定义：dp[i]表示以nums[i]结尾的最大子数组和
- 转移方程：dp[i] = max(dp[i-1] + nums[i], nums[i])
- 空间优化：只需前一个状态，可压缩到O(1)空间

## 示例

```python
def maxSubArray(nums):
    dp = nums[0]
    result = dp
    for i in range(1, len(nums)):
        dp = max(dp + nums[i], nums[i])
        result = max(result, dp)
    return result
```

- 每一步决策：是延续前面的子数组，还是从当前位置重新开始
