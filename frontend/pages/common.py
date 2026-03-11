# filename: frontend/pages/common.py
"""通用页面组件"""
from __future__ import annotations

import json
from typing import Any, Dict, Optional

import streamlit as st


def render_ai_teacher_grade(*, title: str, text: str) -> None:
    """
    渲染 AI 老师批改结果。
    
    将 JSON 格式（数学批改）或纯文本格式友好展示。
    """
    if not text:
        return

    # 尝试解析 JSON（数学批改返回严格 JSON）
    clean_text = text.strip()
    if clean_text.startswith("```json"):
        clean_text = clean_text[7:]
    elif clean_text.startswith("```"):
        clean_text = clean_text[3:]
    if clean_text.endswith("```"):
        clean_text = clean_text[:-3]
    clean_text = clean_text.strip()

    obj: Optional[Dict[str, Any]] = None
    try:
        obj = json.loads(clean_text)
    except Exception:
        try:
            obj = json.loads(text)
        except Exception:
            obj = None

    # JSON 格式渲染（数学题批改）
    if isinstance(obj, dict) and {"score", "total"} <= set(obj.keys()):
        score = obj.get("score")
        total = obj.get("total")
        per_step = obj.get("per_step") or []
        overall = (obj.get("overall_comment") or "").strip()
        next_practice = obj.get("next_practice") or []

        st.markdown(
            f'<div class="ai-card"><b>🧑‍🏫 {title}</b></div>',
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns([1, 3])
        with c1:
            st.metric("得分", f"{score}/{total}")
        with c2:
            if overall:
                st.markdown(f"**总体点评**：{overall}")

        if per_step:
            st.markdown("**逐步批改**：")
            for s in per_step:
                sid = (s.get("step_id") or "").strip()
                pts = s.get("points")
                comment = (s.get("comment") or "").strip()
                tags = s.get("mistake_tags") or []
                line = (
                    f"- **Step {sid}**：{pts} 分。{comment}"
                    if sid
                    else f"- **步骤**：{pts} 分。{comment}"
                )
                st.markdown(line)
                if tags:
                    st.caption("错误标签：" + ", ".join([str(t) for t in tags]))

        if next_practice:
            st.markdown("**下一步练习建议**：")
            for it in next_practice:
                st.markdown(f"- {it}")

        return

    # 纯文本渲染
    safe = text.replace("\n", "<br>")
    st.markdown(
        f'<div class="ai-card"><b>🧑‍🏫 {title}</b><br>{safe}</div>',
        unsafe_allow_html=True,
    )

