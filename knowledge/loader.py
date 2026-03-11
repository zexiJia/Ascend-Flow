"""Knowledge nodes loader.

Loads JSON files under:
- `knowledge/node_specs/*.json` (preferred)
- `knowledge/nodes/*.json` (legacy, kept for compatibility)
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict
from typing import Dict, List, Optional

from knowledge.models import KnowledgeContent, KnowledgeNode
from knowledge.paths import find_dir, resolve_content_ref

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_NODES_DIR, _NODES_DIR_MODE = find_dir("node_specs", "nodes")

_CACHE_BY_ID: Optional[Dict[str, KnowledgeNode]] = None


def _load_nodes_from_file(path: str) -> List[KnowledgeNode]:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    out: List[KnowledgeNode] = []
    for r in raw:
        c = r.get("content") or {}
        content = KnowledgeContent(
            content_ref=resolve_content_ref(c.get("content_ref", "") or ""),
            content_summary=c.get("content_summary", "") or "",
            learning_objectives=c.get("learning_objectives", []) or [],
            key_takeaways=c.get("key_takeaways", []) or [],
            worked_examples_refs=c.get("worked_examples_refs", []) or [],
            quick_checks_refs=c.get("quick_checks_refs", []) or [],
        )
        out.append(
            KnowledgeNode(
                node_id=r.get("node_id", "") or "",
                subject=r.get("subject", "") or "",
                level=r.get("level", "") or "",
                type=r.get("type", "") or "",
                name=r.get("name", "") or "",
                difficulty=int(r.get("difficulty", 0) or 0),
                parents=r.get("parents", []) or [],
                prereq=r.get("prereq", []) or [],
                tags=r.get("tags", []) or [],
                common_mistakes=r.get("common_mistakes", []) or [],
                content=content,
                version=r.get("version", "v1") or "v1",
            )
        )
    return out


def _ensure_loaded() -> Dict[str, KnowledgeNode]:
    global _CACHE_BY_ID
    if _CACHE_BY_ID is not None:
        return _CACHE_BY_ID

    by_id: Dict[str, KnowledgeNode] = {}
    if not os.path.isdir(_NODES_DIR):
        _CACHE_BY_ID = {}
        return _CACHE_BY_ID

    for fn in os.listdir(_NODES_DIR):
        if not fn.endswith(".json"):
            continue
        path = os.path.join(_NODES_DIR, fn)
        for n in _load_nodes_from_file(path):
            if not n.node_id:
                continue
            if n.node_id in by_id:
                raise ValueError(f"Duplicate node_id: {n.node_id}")
            by_id[n.node_id] = n

    _CACHE_BY_ID = by_id
    return by_id


# ============ Public API ============

def get_all_nodes() -> List[KnowledgeNode]:
    """Get all knowledge nodes."""
    return list(_ensure_loaded().values())


# Alias
get_all_knowledge_nodes = get_all_nodes


def get_node_by_id(node_id: str) -> Optional[KnowledgeNode]:
    """Get a knowledge node by its ID."""
    return _ensure_loaded().get(node_id)


# Alias
get_knowledge_node_by_id = get_node_by_id


def get_nodes_by_subject(subject: str) -> List[KnowledgeNode]:
    """Get all nodes for a given subject (coding/math/deeplearning)."""
    subject = (subject or "").strip()
    return [n for n in get_all_nodes() if n.subject == subject]


# Alias
get_knowledge_nodes_by_subject = get_nodes_by_subject


def get_nodes_by_level(level: str) -> List[KnowledgeNode]:
    """Get all nodes at a given level (macro/meso/micro)."""
    level = (level or "").strip().lower()
    return [n for n in get_all_nodes() if n.level == level]


# Alias
get_knowledge_nodes_by_level = get_nodes_by_level


def get_nodes_by_tags(tags: List[str]) -> List[KnowledgeNode]:
    """Get nodes matching any of the given tags."""
    tag_set = set(t.lower() for t in tags if t)
    return [n for n in get_all_nodes() if any(t.lower() in tag_set for t in n.tags)]


# Alias
get_knowledge_nodes_by_tags = get_nodes_by_tags


def dump_debug() -> Dict[str, Dict]:
    """For debugging only: returns JSON-serializable snapshot."""
    return {k: asdict(v) for k, v in _ensure_loaded().items()}
