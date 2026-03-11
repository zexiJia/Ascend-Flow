# filename: frontend/components/__init__.py
"""Frontend components - UI components, cards, badges, stepper, avatars, AI chat"""

from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Literal, Optional, List

import streamlit as st

# AI Chat component
from frontend.components.ai_chat import render_ai_teacher_chat

Status = Literal["done", "now", "next"]


@dataclass(frozen=True)
class StepItem:
    key: str
    title: str
    status: Status


def badge(status: Status) -> str:
    if status == "done":
        return '<span class="af-badge af-badge-done">Done</span>'
    if status == "now":
        return '<span class="af-badge af-badge-now">Now</span>'
    return '<span class="af-badge af-badge-next">Next</span>'


def render_stepper(steps: List[StepItem]) -> None:
    blocks = []
    for s in steps:
        blocks.append(
            f"""
            <div class="af-step">
              <div class="af-step-title">{s.title}</div>
              <div class="af-step-sub">{badge(s.status)}</div>
            </div>
            """
        )
    st.markdown(f'<div class="af-stepper">{"".join(blocks)}</div>', unsafe_allow_html=True)


def card(title: str, body_md: str, *, chips: Optional[List[str]] = None) -> None:
    chips_html = ""
    if chips:
        chips_html = '<div class="af-card-row">' + "".join([f'<span class="af-chip">{c}</span>' for c in chips]) + "</div>"
    st.markdown(
        f"""
        <div class="af-card">
          <div class="af-card-title">{title}</div>
          <div class="af-muted">{body_md}</div>
          {chips_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def avatar_data_uri(letter: str, color_hex: str) -> str:
    letter = (letter or "?")[:1].upper()
    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="96" height="96" viewBox="0 0 96 96">
      <defs>
        <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="{color_hex}" stop-opacity="0.96"/>
          <stop offset="1" stop-color="#111827" stop-opacity="0.08"/>
        </linearGradient>
      </defs>
      <circle cx="48" cy="48" r="44" fill="url(#g)"/>
      <text x="48" y="56" text-anchor="middle" font-size="42" font-family="ui-sans-serif, system-ui, -apple-system" fill="#ffffff" font-weight="700">{letter}</text>
    </svg>
    """.strip()
    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{b64}"


def role_avatar(role: str) -> str:
    role = (role or "").lower()
    mapping = {
        "planner": ("P", "#5B7CFA"),
        "tutor": ("T", "#22C55E"),
        "examiner": ("E", "#F59E0B"),
        "reviewer": ("R", "#EF4444"),
        "motivator": ("M", "#A855F7"),
        "scribe": ("S", "#06B6D4"),
        "manager": ("G", "#64748B"),
    }
    letter, color = mapping.get(role, ("?", "#64748B"))
    return avatar_data_uri(letter, color)


__all__ = [
    "StepItem",
    "badge",
    "render_stepper",
    "card",
    "avatar_data_uri",
    "role_avatar",
    "render_ai_teacher_chat",
]

