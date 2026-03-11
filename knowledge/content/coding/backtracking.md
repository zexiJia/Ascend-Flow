# 回溯算法

回溯算法是一种通过探索所有可能的候选解来找出所有解的算法。如果候选解被确认不是一个解（或者至少不是最后一个解），回溯算法会通过在上一步进行一些变化丢弃该解，即「回溯」并且再次尝试。

## 核心要点

- 核心思想：深度优先搜索(DFS) + 剪枝
- 适用场景：排列、组合、子集、棋盘问题
- 三要素：路径（已做的选择）、选择列表（可做的选择）、结束条件
- 回溯模板：做选择 → 递归 → 撤销选择
- 剪枝优化：提前判断不满足条件的分支，减少搜索空间
- 与动态规划区别：回溯穷举所有可能，DP存在最优子结构

## 示例

```python
# 回溯算法通用模板
def backtrack(path, choices):
    if 满足结束条件:
        result.append(path[:])
        return
    
    for choice in choices:
        # 做选择
        path.append(choice)
        # 递归
        backtrack(path, 新的选择列表)
        # 撤销选择（回溯）
        path.pop()
```

- 回溯的精髓：在递归之前「做选择」，在递归之后「撤销选择」

```python
# 全排列问题
def permute(nums):
    result = []
    def backtrack(path, used):
        if len(path) == len(nums):
            result.append(path[:])
            return
        for i, num in enumerate(nums):
            if used[i]:
                continue
            path.append(num)
            used[i] = True
            backtrack(path, used)
            path.pop()
            used[i] = False
    backtrack([], [False] * len(nums))
    return result
```

- 全排列：用used数组记录哪些元素已被使用

```python
# 组合问题
def combine(n, k):
    result = []
    def backtrack(start, path):
        if len(path) == k:
            result.append(path[:])
            return
        for i in range(start, n + 1):
            path.append(i)
            backtrack(i + 1, path)  # 从i+1开始避免重复
            path.pop()
    backtrack(1, [])
    return result
```

- 组合：通过start参数保证不选重复元素

```python
# N皇后问题
def solveNQueens(n):
    result = []
    board = [['.' for _ in range(n)] for _ in range(n)]
    
    def is_valid(row, col):
        # 检查列
        for i in range(row):
            if board[i][col] == 'Q':
                return False
        # 检查左上对角线
        i, j = row - 1, col - 1
        while i >= 0 and j >= 0:
            if board[i][j] == 'Q':
                return False
            i, j = i - 1, j - 1
        # 检查右上对角线
        i, j = row - 1, col + 1
        while i >= 0 and j < n:
            if board[i][j] == 'Q':
                return False
            i, j = i - 1, j + 1
        return True
    
    def backtrack(row):
        if row == n:
            result.append([''.join(r) for r in board])
            return
        for col in range(n):
            if not is_valid(row, col):
                continue
            board[row][col] = 'Q'
            backtrack(row + 1)
            board[row][col] = '.'  # 回溯
    
    backtrack(0)
    return result
```

- N皇后：经典回溯题，每行放一个皇后，检查列和对角线冲突
