# filename: frontend/pages/library.py
"""题库页面渲染"""

from __future__ import annotations

import streamlit as st

from problems.coding.loader import get_coding_items
from problems.math.loader import get_math_items
from problems.deeplearning.loader import get_dl_items
from frontend.state import go_to_problem
from frontend.ui_utils import difficulty_to_badge


# 题型中文名
PROBLEM_TYPE_NAMES = {
    "single_choice": "单选题",
    "multi_choice": "多选题",
    "fill": "填空题",
    "code": "代码题",
    "short_answer": "简答题",
}


def render_library() -> None:
    """渲染题库页面"""
    cat = st.session_state.library_category

    if cat == "coding":
        _render_coding_library()
    elif cat == "math":
        _render_math_library()
    elif cat == "deeplearning":
        _render_dl_library()
    else:
        _render_all_library()


def _render_all_library() -> None:
    """渲染全部题库"""
    st.markdown("## 📚 题库")
    
    tabs = st.tabs(["💻 编程题", "📐 数学题", "🧠 深度学习题"])
    
    with tabs[0]:
        _render_coding_library(show_title=False)
    with tabs[1]:
        _render_math_library(show_title=False)
    with tabs[2]:
        _render_dl_library(show_title=False)


def _render_coding_library(show_title: bool = True) -> None:
    if show_title:
        st.markdown("## 💻 编程题库")

    items = get_coding_items()
    st.caption(f"共 {len(items)} 道题目")

    for p in items:
        c1, c2, c3 = st.columns([4, 1, 1])

        with c1:
            st.markdown(f"**{p.title}**")
            if p.tags:
                st.caption(" / ".join(p.tags[:4]))
        with c2:
            cls, label = difficulty_to_badge(p.difficulty)
            st.markdown(f'<span style="background:#f3f4f6;color:#6b7280;padding:4px 10px;border-radius:6px;font-size:0.8rem;">{label}</span>', unsafe_allow_html=True)
        with c3:
            if st.button("开始练习", key=f"lib_c_{p.item_id}"):
                go_to_problem("coding", p.item_id)
                st.rerun()

        st.markdown("---")


def _render_math_library(show_title: bool = True) -> None:
    if show_title:
        st.markdown("## 📐 数学题库")

    items = get_math_items()
    st.caption(f"共 {len(items)} 道题目")

    for p in items:
        c1, c2, c3 = st.columns([4, 1, 1])

        with c1:
            st.markdown(f"**{p.title}**")
            # 显示简短的题目描述
            if hasattr(p, 'prompt') and p.prompt:
                prompt_short = p.prompt[:80] + "..." if len(p.prompt) > 80 else p.prompt
                st.caption(prompt_short)
        with c2:
            cls, label = difficulty_to_badge(p.difficulty)
            st.markdown(f'<span style="background:#f3f4f6;color:#6b7280;padding:4px 10px;border-radius:6px;font-size:0.8rem;">{label}</span>', unsafe_allow_html=True)
        with c3:
            if st.button("开始练习", key=f"lib_m_{p.item_id}"):
                go_to_problem("math", p.item_id)
                st.rerun()

        st.markdown("---")


def _render_dl_library(show_title: bool = True) -> None:
    if show_title:
        st.markdown("## 🧠 深度学习题库")

    items = get_dl_items()
    st.caption(f"共 {len(items)} 道题目")

    for p in items:
        c1, c2, c3 = st.columns([4, 1, 1])

        with c1:
            st.markdown(f"**{p.title}**")
            ptype_name = PROBLEM_TYPE_NAMES.get(p.problem_type, p.problem_type)
            tags_str = " / ".join((p.tags or [])[:3])
            st.caption(f"{ptype_name} | {tags_str}" if tags_str else ptype_name)
        with c2:
            cls, label = difficulty_to_badge(p.difficulty)
            st.markdown(f'<span style="background:#f3f4f6;color:#6b7280;padding:4px 10px;border-radius:6px;font-size:0.8rem;">{label}</span>', unsafe_allow_html=True)
        with c3:
            if st.button("开始练习", key=f"lib_dl_{p.item_id}"):
                go_to_problem("deeplearning", p.item_id)
                st.rerun()

        st.markdown("---")
