# 链表操作技巧

链表是一种动态数据结构，节点通过指针连接。掌握链表的遍历、插入、删除和合并是解决链表问题的基础。

## 核心要点

- 链表节点结构：val + next指针
- 虚拟头节点(dummy)简化边界处理
- 双指针技巧在链表中的应用
- 递归与迭代两种思路

## 示例

```python
def mergeTwoLists(l1, l2):
    dummy = ListNode(0)
    curr = dummy
    while l1 and l2:
        if l1.val <= l2.val:
            curr.next = l1
            l1 = l1.next
        else:
            curr.next = l2
            l2 = l2.next
        curr = curr.next
    curr.next = l1 or l2
    return dummy.next
```

- 使用dummy节点避免处理头节点的特殊情况，比较选择较小节点
