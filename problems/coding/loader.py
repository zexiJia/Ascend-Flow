"""Coding items loader - Item schema v1."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROBLEMS_JSON = os.path.join(_THIS_DIR, "problems.json")

def _clean_evidence(ev: str) -> str:
    ev = (ev or "").strip()
    if not ev:
        return ""
    if ev.startswith("来自旧字段"):
        return ""
    return ev


@dataclass(frozen=True)
class KnowledgeLink:
    node_id: str
    role: str  # primary|secondary|transfer_check
    weight: int = 1
    evidence: str = ""


@dataclass(frozen=True)
class CodingItem:
    item_id: str
    title: str
    domain: str
    format: str
    prompt: str
    difficulty: int
    estimated_time_min: int
    tags: List[str] = field(default_factory=list)
    grader: Dict[str, Any] = field(default_factory=dict)
    variation_axes: List[str] = field(default_factory=list)
    knowledge_links: List[KnowledgeLink] = field(default_factory=list)
    version: str = "v1"

    function_name: str = ""
    function_signature: str = ""
    starter_code: str = ""
    hints: Dict[int, str] = field(default_factory=dict)
    explanation: str = ""


def _load_raw() -> List[Dict[str, Any]]:
    with open(_PROBLEMS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def get_coding_items() -> List[CodingItem]:
    items: List[CodingItem] = []
    for p in _load_raw():
        hints_raw = p.get("hints", {}) or {}
        hints = {int(k): v for k, v in hints_raw.items()} if isinstance(hints_raw, dict) else {}

        links_raw = p.get("knowledge_links", []) or []
        links = [
            KnowledgeLink(
                node_id=str(x.get("node_id", "") or ""),
                role=str(x.get("role", "primary") or "primary"),
                weight=int(x.get("weight", 1) or 1),
                evidence=_clean_evidence(str(x.get("evidence", "") or "")),
            )
            for x in links_raw
            if isinstance(x, dict)
        ]

        items.append(
            CodingItem(
                item_id=str(p.get("item_id") or ""),
                title=str(p.get("title", "") or ""),
                domain=str(p.get("domain", "coding") or "coding"),
                format=str(p.get("format", "coding_function") or "coding_function"),
                prompt=str(p.get("prompt", "") or ""),
                difficulty=int(p.get("difficulty", 0) or 0),
                estimated_time_min=int(p.get("estimated_time_min", 0) or 0),
                tags=p.get("tags", []) or [],
                grader=p.get("grader", {}) or {},
                variation_axes=p.get("variation_axes", []) or [],
                knowledge_links=links,
                version=str(p.get("version", "v1") or "v1"),
                function_name=str(p.get("function_name", "") or ""),
                function_signature=str(p.get("function_signature", "") or ""),
                starter_code=str(p.get("starter_code", "") or ""),
                hints=hints,
                explanation=str(p.get("explanation", "") or ""),
            )
        )
    return items


def get_coding_item_by_id(item_id: str) -> Optional[CodingItem]:
    for p in get_coding_items():
        if p.item_id == item_id:
            return p
    return None


def get_coding_items_by_tags(tags: List[str]) -> List[CodingItem]:
    if not tags:
        return []
    items = get_coding_items()
    return [p for p in items if any(tag in p.tags for tag in tags)]
