"""Reusable panels for item pages: knowledge + prereqs + similar items."""

from __future__ import annotations

import streamlit as st

from knowledge.graph import get_ancestors, get_prereqs
from knowledge.loader import get_node_by_id
from services.recommendations import get_similar_items
from frontend.state import go_to_problem, go_to_knowledge_detail


# 颜色和中文标签
LEVEL_COLORS = {
    "macro": "#667eea",
    "meso": "#10b981",
    "micro": "#f59e0b",
}

LEVEL_LABELS = {
    "macro": "一级",
    "meso": "二级",
    "micro": "三级",
}

ROLE_LABELS = {
    "primary": "主要",
    "secondary": "次要",
}


def render_item_knowledge_panel(*, domain: str, item_id: str, knowledge_links) -> None:
    """Render: linked knowledge nodes + ancestors + prereqs."""

    links = list(knowledge_links or [])
    if not links:
        st.caption("（该题暂未绑定知识点）")
        return

    st.markdown("**归属知识点**")
    for lk in links:
        n = get_node_by_id(getattr(lk, "node_id", ""))
        name = n.name if n else "未知"
        role = getattr(lk, "role", "primary")
        role_label = ROLE_LABELS.get(role, role)
        level_label = LEVEL_LABELS.get(n.level, "") if n else ""
        color = LEVEL_COLORS.get(n.level, "#6b7280") if n else "#6b7280"
        
        st.markdown(f"""
        <div style="background:{color}10;border-left:3px solid {color};padding:0.5rem;margin-bottom:0.5rem;border-radius:4px;">
            <span style="font-weight:600;">{name}</span>
            <span style="background:{color}20;color:{color};padding:2px 6px;border-radius:4px;font-size:0.7rem;margin-left:0.5rem;">{level_label}</span>
            <span style="background:#f3f4f6;color:#6b7280;padding:2px 6px;border-radius:4px;font-size:0.7rem;margin-left:0.25rem;">{role_label}</span>
        </div>
        """, unsafe_allow_html=True)
        
        if n:
            if st.button(f"查看知识点详情", key=f"kp_{lk.node_id}_{item_id}", use_container_width=True):
                go_to_knowledge_detail(n.node_id)
                st.rerun()
        
        # 不展示旧字段迁移痕迹（例如“来自旧字段 …”），避免干扰学习体验

    primary_nodes = [lk.node_id for lk in links if getattr(lk, "role", "primary") == "primary"]
    if not primary_nodes:
        primary_nodes = [lk.node_id for lk in links]

    ancestor_nodes = []
    prereq_nodes = []
    seen_a = set()
    seen_p = set()

    for nid in primary_nodes:
        for a in get_ancestors(nid, include_self=False):
            if a.node_id not in seen_a:
                seen_a.add(a.node_id)
                ancestor_nodes.append(a)
        for p in get_prereqs(nid, transitive=True):
            if p.node_id not in seen_p:
                seen_p.add(p.node_id)
                prereq_nodes.append(p)

    if ancestor_nodes:
        st.markdown("**上层知识点**")
        for a in ancestor_nodes:
            level_label = LEVEL_LABELS.get(a.level, a.level)
            color = LEVEL_COLORS.get(a.level, "#6b7280")
            st.markdown(f"""
            <div style="padding:0.25rem 0;">
                <span style="color:#4b5563;">📁 {a.name}</span>
                <span style="background:{color}20;color:{color};padding:2px 6px;border-radius:4px;font-size:0.7rem;margin-left:0.5rem;">{level_label}</span>
            </div>
            """, unsafe_allow_html=True)

    if prereq_nodes:
        st.markdown("**前置知识点**")
        for p in prereq_nodes:
            level_label = LEVEL_LABELS.get(p.level, p.level)
            color = LEVEL_COLORS.get(p.level, "#6b7280")
            st.markdown(f"""
            <div style="padding:0.25rem 0;">
                <span style="color:#4b5563;">📋 {p.name}</span>
                <span style="background:{color}20;color:{color};padding:2px 6px;border-radius:4px;font-size:0.7rem;margin-left:0.5rem;">{level_label}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.caption("（暂无前置知识点要求）")


def render_similar_items_panel(*, domain: str, item_id: str, title: str = "相似题推荐") -> None:
    sims = get_similar_items(domain, item_id, top_k=6)
    if not sims:
        st.caption("（暂无相似题推荐）")
        return

    st.markdown(f"**{title}** (共 {len(sims)} 题)")

    from problems.coding.loader import get_coding_item_by_id
    from problems.math.loader import get_math_item_by_id
    from problems.deeplearning.loader import get_dl_item_by_id

    domain_icons = {"coding": "💻", "math": "📐", "deeplearning": "🧠"}
    icon = domain_icons.get(domain, "📝")

    for s in sims:
        if domain == "coding":
            it = get_coding_item_by_id(s.item_id)
        elif domain == "math":
            it = get_math_item_by_id(s.item_id)
        else:
            it = get_dl_item_by_id(s.item_id)
        if not it:
            continue

        # 获取共享知识点的中文名称
        shared_names = []
        for node_id in s.shared_nodes[:2]:
            n = get_node_by_id(node_id)
            if n:
                shared_names.append(n.name)
        shared_str = "、".join(shared_names) if shared_names else ""
        
        st.markdown(f"""
        <div style="background:white;border:1px solid #e5e7eb;border-radius:8px;padding:0.5rem 0.75rem;margin-bottom:0.5rem;">
            <div style="font-weight:500;color:#1f2937;">{icon} {it.title}</div>
            {f'<div style="font-size:0.75rem;color:#9ca3af;">共享知识点：{shared_str}</div>' if shared_str else ''}
        </div>
        """, unsafe_allow_html=True)
        
        btn = st.button(
            f"开始练习",
            key=f"sim_{item_id}_{it.item_id}",
            use_container_width=True,
        )
        if btn:
            go_to_problem(domain, it.item_id)
            st.rerun()
