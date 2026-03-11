# 数组与双指针技巧

双指针是处理数组问题的常用技巧，通过两个指针从不同位置或方向遍历数组，可以将O(n²)的暴力解法优化到O(n)。

## 核心要点

- 对撞指针：两端向中间移动
- 快慢指针：同向不同速度移动
- 滑动窗口：维护一个动态区间
- 适用场景：有序数组、链表环检测、子数组问题

## 示例

```python
# 对撞指针找两数之和
left, right = 0, len(nums) - 1
while left < right:
    s = nums[left] + nums[right]
    if s == target:
        return [left, right]
    elif s < target:
        left += 1
    else:
        right -= 1
```

- 在有序数组中，利用单调性移动指针，避免枚举所有组合
