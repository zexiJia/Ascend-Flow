"""Item recommendation helpers.

Currently:
- Similar items within the same domain based on overlap of linked knowledge nodes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from problems.coding.loader import get_coding_items
from problems.deeplearning.loader import get_dl_items
from problems.math.loader import get_math_items


@dataclass(frozen=True)
class SimilarItem:
    item_id: str
    score: float
    shared_nodes: List[str]


def _node_ids(links: Iterable) -> List[str]:
    out: List[str] = []
    for lk in links or []:
        nid = getattr(lk, "node_id", None)
        if nid:
            out.append(str(nid))
    return out


def _domain_items(domain: str):
    if domain == "coding":
        return list(get_coding_items())
    if domain == "math":
        return list(get_math_items())
    if domain == "deeplearning":
        return list(get_dl_items())
    return []


def get_similar_items(domain: str, item_id: str, *, top_k: int = 6) -> List[SimilarItem]:
    items = _domain_items(domain)
    base = None
    for it in items:
        if getattr(it, "item_id", None) == item_id:
            base = it
            break
    if base is None:
        return []

    base_nodes = set(_node_ids(getattr(base, "knowledge_links", [])))
    if not base_nodes:
        return []

    scored: List[SimilarItem] = []
    for it in items:
        if it.item_id == item_id:
            continue
        nodes = set(_node_ids(getattr(it, "knowledge_links", [])))
        if not nodes:
            continue
        shared = sorted(base_nodes & nodes)
        if not shared:
            continue
        j = len(shared) / max(len(base_nodes | nodes), 1)
        score = j * 10.0 + len(shared)
        scored.append(SimilarItem(item_id=it.item_id, score=score, shared_nodes=shared))

    scored.sort(key=lambda x: (-x.score, x.item_id))
    return scored[: max(int(top_k), 0)]
