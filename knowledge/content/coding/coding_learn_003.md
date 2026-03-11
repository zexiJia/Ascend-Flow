# 栈的应用：括号匹配

栈是一种后进先出(LIFO)的数据结构，非常适合处理「匹配」类问题，如括号匹配、表达式求值等。

## 核心要点

- 栈的基本操作：push, pop, peek
- 括号匹配的核心：遇左括号入栈，遇右括号出栈匹配
- Python用list模拟栈：append()入栈，pop()出栈
- 边界情况：空栈时pop、遍历结束栈非空

## 示例

```python
def isValid(s):
    stack = []
    mapping = {')': '(', ']': '[', '}': '{'}
    for c in s:
        if c in mapping:
            if not stack or stack.pop() != mapping[c]:
                return False
        else:
            stack.append(c)
    return len(stack) == 0
```

- 用字典存储括号配对关系，遇到右括号时检查栈顶是否匹配
