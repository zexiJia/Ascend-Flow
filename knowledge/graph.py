"""Graph utilities for knowledge nodes."""

from __future__ import annotations

from collections import deque
from typing import Dict, List, Set, Tuple

from knowledge.loader import get_all_knowledge_nodes, get_knowledge_node_by_id
from knowledge.models import KnowledgeNode


def _index_by_id() -> Dict[str, KnowledgeNode]:
    return {n.node_id: n for n in get_all_knowledge_nodes() if n.node_id}


def get_ancestors(node_id: str, *, include_self: bool = False, max_depth: int = 20) -> List[KnowledgeNode]:
    """Return ancestors following `parents` links (deduped)."""
    by_id = _index_by_id()
    if node_id not in by_id:
        return []

    seen: Set[str] = set()
    out: List[KnowledgeNode] = []

    q = deque([(node_id, 0)])
    while q:
        nid, d = q.popleft()
        if nid in seen:
            continue
        seen.add(nid)

        n = by_id.get(nid)
        if not n:
            continue

        if include_self or nid != node_id:
            out.append(n)

        if d >= max_depth:
            continue
        for p in n.parents:
            if p and p not in seen:
                q.append((p, d + 1))

    level_rank = {"micro": 0, "meso": 1, "macro": 2}
    out.sort(key=lambda x: (level_rank.get(x.level, 9), x.node_id))
    return out


def get_prereqs(node_id: str, *, transitive: bool = True, max_depth: int = 20) -> List[KnowledgeNode]:
    """Return prerequisites following `prereq` links."""
    by_id = _index_by_id()
    if node_id not in by_id:
        return []

    seen: Set[str] = set()
    out: List[KnowledgeNode] = []

    q = deque([(node_id, 0)])
    while q:
        nid, d = q.popleft()
        n = by_id.get(nid)
        if not n:
            continue

        for pre in n.prereq:
            if not pre or pre in seen:
                continue
            seen.add(pre)
            pn = by_id.get(pre)
            if pn:
                out.append(pn)
            if transitive and d < max_depth:
                q.append((pre, d + 1))

        if not transitive:
            break

    level_rank = {"micro": 0, "meso": 1, "macro": 2}
    out.sort(key=lambda x: (level_rank.get(x.level, 9), x.node_id))
    return out


def get_children(node_id: str) -> List[KnowledgeNode]:
    """Return direct children (nodes whose `parents` contain node_id)."""
    by_id = _index_by_id()
    out = []
    for n in by_id.values():
        if node_id in n.parents:
            out.append(n)
    level_rank = {"macro": 0, "meso": 1, "micro": 2}
    out.sort(key=lambda x: (level_rank.get(x.level, 9), x.node_id))
    return out


def get_descendants(node_id: str, *, max_depth: int = 20) -> List[KnowledgeNode]:
    """Return all descendants (children, grandchildren, etc.)."""
    by_id = _index_by_id()
    if node_id not in by_id:
        return []

    # Build parent->children index
    children_of: Dict[str, List[str]] = {}
    for n in by_id.values():
        for p in n.parents:
            children_of.setdefault(p, []).append(n.node_id)

    seen: Set[str] = set()
    out: List[KnowledgeNode] = []

    q = deque([(node_id, 0)])
    while q:
        nid, d = q.popleft()
        for child_id in children_of.get(nid, []):
            if child_id in seen:
                continue
            seen.add(child_id)
            cn = by_id.get(child_id)
            if cn:
                out.append(cn)
            if d < max_depth:
                q.append((child_id, d + 1))

    level_rank = {"macro": 0, "meso": 1, "micro": 2}
    out.sort(key=lambda x: (level_rank.get(x.level, 9), x.node_id))
    return out


def get_items_for_node(node_id: str) -> List[Tuple[str, str]]:
    """
    Return list of (item_id, domain) tuples for items linked to this node.
    Searches all problem domains for items whose knowledge_links contain node_id.
    """
    from problems.coding.loader import get_coding_items
    from problems.math.loader import get_math_items
    from problems.deeplearning.loader import get_dl_items

    results: List[Tuple[str, str]] = []

    for item in get_coding_items():
        for link in item.knowledge_links:
            if link.node_id == node_id:
                results.append((item.item_id, "coding"))
                break

    for item in get_math_items():
        for link in item.knowledge_links:
            if link.node_id == node_id:
                results.append((item.item_id, "math"))
                break

    for item in get_dl_items():
        for link in item.knowledge_links:
            if link.node_id == node_id:
                results.append((item.item_id, "deeplearning"))
                break

    return results


def get_similar_items(item_id: str, domain: str, limit: int = 5) -> List[Tuple[str, str]]:
    """
    Return similar items based on shared micro knowledge links.
    """
    from problems.coding.loader import get_coding_items, get_coding_item_by_id
    from problems.math.loader import get_math_items, get_math_item_by_id
    from problems.deeplearning.loader import get_dl_items, get_dl_item_by_id

    # Get current item's micro links
    if domain == "coding":
        item = get_coding_item_by_id(item_id)
    elif domain == "math":
        item = get_math_item_by_id(item_id)
    else:
        item = get_dl_item_by_id(item_id)

    if not item:
        return []

    micro_ids = set()
    for link in item.knowledge_links:
        node = get_knowledge_node_by_id(link.node_id)
        if node and node.level == "micro":
            micro_ids.add(link.node_id)

    if not micro_ids:
        return []

    # Find items sharing micro links
    candidates: List[Tuple[str, str, int]] = []  # (item_id, domain, overlap_count)

    all_items = [
        (get_coding_items(), "coding"),
        (get_math_items(), "math"),
        (get_dl_items(), "deeplearning"),
    ]

    for items, d in all_items:
        for it in items:
            if it.item_id == item_id and d == domain:
                continue
            overlap = 0
            for link in it.knowledge_links:
                if link.node_id in micro_ids:
                    overlap += 1
            if overlap > 0:
                candidates.append((it.item_id, d, overlap))

    # Sort by overlap descending
    candidates.sort(key=lambda x: -x[2])
    return [(c[0], c[1]) for c in candidates[:limit]]


def build_graph_data() -> Dict:
    """
    Build graph data structure for visualization.
    Returns {nodes: [...], edges: [...]}
    """
    by_id = _index_by_id()
    
    nodes = []
    edges = []
    
    level_colors = {
        "macro": "#667eea",
        "meso": "#10b981",
        "micro": "#f59e0b",
    }
    
    level_sizes = {
        "macro": 40,
        "meso": 25,
        "micro": 15,
    }
    
    for n in by_id.values():
        nodes.append({
            "id": n.node_id,
            "label": n.name[:20],
            "level": n.level,
            "subject": n.subject,
            "color": level_colors.get(n.level, "#6b7280"),
            "size": level_sizes.get(n.level, 20),
        })
        
        # Parent edges
        for p in n.parents:
            if p in by_id:
                edges.append({
                    "from": p,
                    "to": n.node_id,
                    "type": "parent",
                })
        
        # Prereq edges
        for pre in n.prereq:
            if pre in by_id:
                edges.append({
                    "from": pre,
                    "to": n.node_id,
                    "type": "prereq",
                    "dashes": True,
                })
    
    return {"nodes": nodes, "edges": edges}
