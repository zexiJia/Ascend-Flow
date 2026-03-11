"""Small UI helpers shared across pages."""

from __future__ import annotations


def difficulty_to_badge(difficulty_1_10: int) -> tuple[str, str]:
    """Map numeric difficulty (1-10) to badge class and label."""
    d = int(difficulty_1_10 or 0)
    if d <= 3:
        cls = "easy"
    elif d <= 6:
        cls = "medium"
    else:
        cls = "hard"
    return cls, f"Lv{max(d, 1)}"
