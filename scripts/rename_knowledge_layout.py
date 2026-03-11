"""One-time migration: rename knowledge directories to clearer names.

Target layout (preferred):
- knowledge/node_specs/   (was knowledge/nodes/)
- knowledge/materials/    (was knowledge/content/)
- knowledge/assets/       (keep as-is for now)

Also updates JSON content_ref prefix:
- knowledge/content/...   -> knowledge/materials/...

Usage:
  python scripts/rename_knowledge_layout.py
"""

from __future__ import annotations

import json
import os
import shutil
from typing import List


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE_DIR = os.path.join(ROOT, "knowledge")


def _rename_dir(src: str, dst: str) -> None:
    if os.path.isdir(dst):
        return
    if not os.path.isdir(src):
        return
    shutil.move(src, dst)


def _rewrite_json_files(json_dir: str) -> None:
    if not os.path.isdir(json_dir):
        return
    for fn in os.listdir(json_dir):
        if not fn.endswith(".json"):
            continue
        path = os.path.join(json_dir, fn)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        changed = False
        for node in data:
            c = node.get("content") or {}
            ref = (c.get("content_ref") or "").replace("\\", "/")
            if ref.startswith("knowledge/content/"):
                c["content_ref"] = ref.replace("knowledge/content/", "knowledge/materials/")
                node["content"] = c
                changed = True
        if changed:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)


def main() -> None:
    nodes_legacy = os.path.join(KNOWLEDGE_DIR, "nodes")
    nodes_new = os.path.join(KNOWLEDGE_DIR, "node_specs")
    content_legacy = os.path.join(KNOWLEDGE_DIR, "content")
    content_new = os.path.join(KNOWLEDGE_DIR, "materials")

    _rename_dir(nodes_legacy, nodes_new)
    _rename_dir(content_legacy, content_new)

    # After renaming, update JSON in the new location if present; otherwise legacy.
    json_dir = nodes_new if os.path.isdir(nodes_new) else nodes_legacy
    _rewrite_json_files(json_dir)

    print("✅ knowledge layout migration done.")
    print("   - node specs:", "node_specs" if os.path.isdir(nodes_new) else "nodes")
    print("   - materials :", "materials" if os.path.isdir(content_new) else "content")


if __name__ == "__main__":
    main()


