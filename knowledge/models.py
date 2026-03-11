"""Dataclasses for the Macro/Meso/Micro knowledge node graph."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class KnowledgeContent:
    content_ref: str = ""
    content_summary: str = ""
    learning_objectives: List[str] = field(default_factory=list)
    key_takeaways: List[str] = field(default_factory=list)
    worked_examples_refs: List[str] = field(default_factory=list)
    quick_checks_refs: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class KnowledgeNode:
    node_id: str
    subject: str  # "coding" | "math" | "deeplearning"
    level: str  # "macro" | "meso" | "micro"
    type: str  # "skill" | "concept" | "rep"
    name: str
    difficulty: int
    parents: List[str] = field(default_factory=list)
    prereq: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    common_mistakes: List[str] = field(default_factory=list)
    content: KnowledgeContent = field(default_factory=KnowledgeContent)
    version: str = "v1"
