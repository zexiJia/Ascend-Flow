"""Knowledge data layout paths.

We keep compatibility with the legacy layout:
- knowledge/nodes/        (legacy)  -> knowledge/node_specs/ (preferred)
- knowledge/content/      (legacy)  -> knowledge/materials/  (preferred)
- knowledge/assets/       (current) -> (keep as-is for now)

The repo may be in either state depending on whether the migration script
`scripts/rename_knowledge_layout.py` has been run.
"""

from __future__ import annotations

import os
from typing import Tuple


def knowledge_root() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def find_dir(preferred: str, legacy: str) -> Tuple[str, str]:
    """Return (dir_path, mode) where mode in {"preferred","legacy","missing"}."""
    root = knowledge_root()
    p = os.path.join(root, preferred)
    if os.path.isdir(p):
        return p, "preferred"
    l = os.path.join(root, legacy)
    if os.path.isdir(l):
        return l, "legacy"
    return p, "missing"


def resolve_content_ref(content_ref: str) -> str:
    """Map old/new content_ref prefixes to the currently-existing directory."""
    s = (content_ref or "").strip()
    if not s:
        return s

    # Normalize to forward slashes for prefix checks
    norm = s.replace("\\", "/")

    materials_dir, mode = find_dir("materials", "content")
    if mode == "preferred":
        return norm.replace("knowledge/content/", "knowledge/materials/")
    # legacy or missing -> keep legacy prefix
    return norm.replace("knowledge/materials/", "knowledge/content/")


