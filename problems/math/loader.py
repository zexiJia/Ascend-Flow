"""Math items loader - Item schema v1."""

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
    # 去掉旧体系迁移痕迹
    if ev.startswith("来自旧字段"):
        return ""
    return ev


def _normalize_latex(s: str) -> str:
    """将误写成双反斜杠的 LaTeX 规范化为单反斜杠。
    例如：'\\\\int' -> '\\int'，否则 KaTeX 会把其解析成换行 + 普通文本（int/frac 等）。
    """
    s = str(s or "")
    # 仅处理双反斜杠（\\）的情况；正常 LaTeX 应为单反斜杠（\）
    return s.replace("\\\\", "\\")



@dataclass(frozen=True)
class KnowledgeLink:
    node_id: str
    role: str
    weight: int = 1
    evidence: str = ""


@dataclass(frozen=True)
class RubricStep:
    step_id: str
    desc: str
    points: int
    common_mistake_tags: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class MathItem:
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

    category: str = "calculus"
    problem_type: str = "solve"
    options: List[str] = field(default_factory=list)
    correct_option: str = ""
    blanks: Dict[str, List[str]] = field(default_factory=dict)
    rubric: List[RubricStep] = field(default_factory=list)
    expected_answer_latex: str = ""
    explanation: str = ""
    sympy_check: Optional[Dict[str, Any]] = None


def _load_raw() -> List[Dict[str, Any]]:
    with open(_PROBLEMS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def get_math_items() -> List[MathItem]:
    items: List[MathItem] = []
    for p in _load_raw():
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

        rubric_raw = p.get("rubric", []) or []
        rubric = [
            RubricStep(
                step_id=str(s.get("step_id", "") or ""),
                desc=str(s.get("desc", "") or ""),
                points=int(s.get("points", 0) or 0),
                common_mistake_tags=s.get("common_mistake_tags", []) or [],
            )
            for s in rubric_raw
            if isinstance(s, dict)
        ]

        items.append(
            MathItem(
                item_id=str(p.get("item_id") or ""),
                title=str(p.get("title", "") or ""),
                domain=str(p.get("domain", "math") or "math"),
                format=str(p.get("format", "math_solve") or "math_solve"),
                prompt=_normalize_latex(str(p.get("prompt", "") or "")),
                difficulty=int(p.get("difficulty", 0) or 0),
                estimated_time_min=int(p.get("estimated_time_min", 0) or 0),
                tags=p.get("tags", []) or [],
                grader=p.get("grader", {}) or {},
                variation_axes=p.get("variation_axes", []) or [],
                knowledge_links=links,
                version=str(p.get("version", "v1") or "v1"),
                category=str(p.get("category", "calculus") or "calculus"),
                problem_type=str(p.get("problem_type", "solve") or "solve"),
                options=p.get("options", []) or [],
                correct_option=str(p.get("correct_option", "") or ""),
                blanks=p.get("blanks", {}) or {},
                rubric=rubric,
                expected_answer_latex=_normalize_latex(str(p.get("expected_answer_latex", "") or "")),
                explanation=_normalize_latex(str(p.get("explanation", "") or "")),
                sympy_check=p.get("sympy_check"),
            )
        )
    return items


def get_math_item_by_id(item_id: str) -> Optional[MathItem]:
    for p in get_math_items():
        if p.item_id == item_id:
            return p
    return None


def get_math_items_by_tags(tags: List[str]) -> List[MathItem]:
    if not tags:
        return []
    items = get_math_items()
    return [p for p in items if any(tag in p.tags for tag in tags)]
