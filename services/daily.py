"""
每日精选服务 - 基于二级知识点推荐今日练习

架构设计：
- 从二级知识点（meso级别）中随机选取今日知识点主线
- 今日练习根据选中知识点及其下属三级技能点的关联题目生成
- 每个三级技能点至少1道题，最多3道题
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Dict, List, Set, Tuple

from knowledge.loader import get_knowledge_nodes_by_level, get_knowledge_node_by_id
from knowledge.graph import get_items_for_node, get_children
from problems.coding.loader import get_coding_item_by_id
from problems.math.loader import get_math_item_by_id
from problems.deeplearning.loader import get_dl_item_by_id


@dataclass
class KnowledgeInfo:
    """知识点信息（用于今日推荐）"""
    node_id: str
    subject: str  # "coding", "math", "deeplearning"
    name: str
    difficulty: int
    summary: str
    tags: List[str]


# 学科对应的颜色主题
SUBJECT_COLORS = {
    "math": "#667eea",
    "coding": "#10b981",
    "deeplearning": "#f59e0b",
}

SUBJECT_ICONS = {
    "math": "📐",
    "coding": "💻",
    "deeplearning": "🧠",
}

SUBJECT_NAMES = {
    "math": "数学",
    "coding": "编程",
    "deeplearning": "深度学习",
}

# 主题列表
THEMES = [
    "综合训练日",
    "基础巩固日",
    "概念强化日",
    "实践演练日",
    "查漏补缺日",
    "进阶挑战日",
]


def get_featured_knowledge_nodes() -> List[KnowledgeInfo]:
    """获取所有 meso 级别知识点作为今日推荐候选"""
    nodes = []
    for node in get_knowledge_nodes_by_level("meso"):
        content = node.content
        summary = content.content_summary if content else ""
        nodes.append(
            KnowledgeInfo(
                node_id=node.node_id,
                subject=node.subject,
                name=node.name,
                difficulty=node.difficulty,
                summary=summary,
                tags=list(node.tags),
                )
            )
    return nodes


def generate_daily_knowledge(count: int = 3) -> List[KnowledgeInfo]:
    """生成今日知识点主线（每个学科各选一个）"""
    all_nodes = get_featured_knowledge_nodes()
    
    # 按学科分组
    by_subject: Dict[str, List[KnowledgeInfo]] = {}
    for node in all_nodes:
        by_subject.setdefault(node.subject, []).append(node)
    
    selected: List[KnowledgeInfo] = []
    for subject in ["math", "coding", "deeplearning"]:
        candidates = by_subject.get(subject, [])
        if candidates:
            selected.append(random.choice(candidates))

    return selected[:count]


def get_items_for_meso_node(meso_node_id: str, max_per_micro: int = 3) -> List[Tuple[str, str]]:
    """
    获取二级知识点关联的所有题目（包括其下属三级技能点的题目）
    
    规则：
    - 先获取该二级知识点直接关联的题目
    - 再获取其下属每个三级技能点的题目
    - 每个三级技能点最多取 max_per_micro 道题
    """
    items: List[Tuple[str, str]] = []
    seen: Set[str] = set()
    
    # 该二级知识点直接关联的题目
    for item_id, domain in get_items_for_node(meso_node_id):
        if item_id not in seen:
            items.append((item_id, domain))
            seen.add(item_id)
    
    # 下属三级技能点的题目
    micro_children = get_children(meso_node_id)
    for micro in micro_children:
        micro_items = get_items_for_node(micro.node_id)
        count = 0
        for item_id, domain in micro_items:
            if item_id not in seen and count < max_per_micro:
                items.append((item_id, domain))
                seen.add(item_id)
                count += 1
    
    return items


def generate_daily_selection(knowledge_nodes: List[KnowledgeInfo] = None) -> Tuple[List[Dict], str]:
    """
    生成今日练习题目（基于知识点关联）
    
    规则：
    - 根据选中的二级知识点，获取其下属三级技能点的题目
    - 每个三级技能点至少1道，最多3道题目
    """

    if knowledge_nodes is None:
        knowledge_nodes = generate_daily_knowledge()

    picks: List[Dict] = []
    existing_ids: Set[str] = set()

    # 根据知识点获取关联题目
    for kn in knowledge_nodes:
        items = get_items_for_meso_node(kn.node_id, max_per_micro=3)
        for item_id, domain in items:
            if item_id not in existing_ids:
                picks.append({"id": item_id, "type": domain})
                existing_ids.add(item_id)

    # 打乱顺序
    random.shuffle(picks)

    theme = random.choice(THEMES)

    return picks, theme


def knowledge_to_dict(kn: KnowledgeInfo) -> Dict[str, Any]:
    """将 KnowledgeInfo 转换为字典"""
    return {
        "node_id": kn.node_id,
        "subject": kn.subject,
        "name": kn.name,
        "difficulty": kn.difficulty,
        "summary": kn.summary,
        "tags": kn.tags,
        "icon": SUBJECT_ICONS.get(kn.subject, "📖"),
        "color": SUBJECT_COLORS.get(kn.subject, "#6b7280"),
        "subject_name": SUBJECT_NAMES.get(kn.subject, ""),
    }
