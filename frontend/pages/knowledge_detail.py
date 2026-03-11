# filename: frontend/pages/knowledge_detail.py
"""知识点详情页面 - 二级节点作为学习入口，展示三级技能点和题目"""

from __future__ import annotations

import streamlit as st

from knowledge.loader import get_knowledge_node_by_id
from knowledge.graph import get_ancestors, get_prereqs, get_children, get_items_for_node
from problems.coding.loader import get_coding_item_by_id
from problems.math.loader import get_math_item_by_id
from problems.deeplearning.loader import get_dl_item_by_id
from frontend.state import go_to_knowledge_detail, go_to_problem, go_to_knowledge_map, go_home
from frontend.ui_utils import difficulty_to_badge
from frontend.components.ai_chat import render_ai_teacher_chat


# 颜色配置
LEVEL_COLORS = {
    "macro": "#667eea",
    "meso": "#10b981",
    "micro": "#f59e0b",
}

SUBJECT_ICONS = {
    "math": "📐",
    "coding": "💻",
    "deeplearning": "🧠",
}

SUBJECT_NAMES = {
    "math": "数学",
    "coding": "编程",
    "deeplearning": "深度学习",
}

LEVEL_LABELS = {
    "macro": "一级知识点",
    "meso": "二级知识点",
    "micro": "三级技能点",
}


def render_knowledge_detail() -> None:
    """渲染知识点详情页面"""
    node_id = st.session_state.get("current_knowledge_node_id")
    
    if not node_id:
        st.warning("请选择一个知识点")
        if st.button("🗺️ 返回知识地图"):
            go_to_knowledge_map()
            st.rerun()
        return
    
    node = get_knowledge_node_by_id(node_id)
    if not node:
        st.error("知识点不存在")
        if st.button("🗺️ 返回知识地图"):
            go_to_knowledge_map()
            st.rerun()
        return
    
    # 面包屑导航
    _render_breadcrumb(node)
    
    # 标题区域
    icon = SUBJECT_ICONS.get(node.subject, "📖")
    subject_name = SUBJECT_NAMES.get(node.subject, "")
    color = LEVEL_COLORS.get(node.level, "#6b7280")
    level_label = LEVEL_LABELS.get(node.level, "知识点")
    
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1rem;">
        <div style="font-size:2.5rem;">{icon}</div>
        <div>
            <h1 style="margin:0;color:#1f2937;">{node.name}</h1>
            <div style="display:flex;gap:0.5rem;margin-top:0.5rem;">
                <span style="background:{color}20;color:{color};padding:4px 12px;border-radius:6px;font-size:0.8rem;font-weight:600;">{level_label}</span>
                <span style="background:#f3f4f6;color:#6b7280;padding:4px 12px;border-radius:6px;font-size:0.8rem;">{subject_name}</span>
                <span style="background:#f3f4f6;color:#6b7280;padding:4px 12px;border-radius:6px;font-size:0.8rem;">难度 {node.difficulty}/10</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 根据节点层级渲染不同内容
    if node.level == "meso":
        _render_meso_detail(node)
    elif node.level == "micro":
        _render_micro_detail(node)
    else:
        _render_macro_detail(node)


def _render_breadcrumb(node) -> None:
    """渲染面包屑导航"""
    if st.button("🏠 返回首页", key="back_to_home"):
        go_home()
        st.rerun()
    
    ancestors = get_ancestors(node.node_id)
    if ancestors:
        parts = [anc.name for anc in reversed(ancestors)]
        breadcrumb = " → ".join(parts) + f" → **{node.name}**"
        st.markdown(f"<p style='color:#9ca3af;font-size:0.85rem;'>{breadcrumb}</p>", unsafe_allow_html=True)


def _render_meso_detail(node) -> None:
    """渲染二级知识点详情 - 作为学习入口"""
    content = node.content
    
    # 知识点概述
    if content and content.content_summary:
        st.markdown("### 📝 学习内容概述")
        st.markdown(content.content_summary)
    
    # 核心要点
    if content and content.key_takeaways:
        st.markdown("### 🎯 核心要点")
        for point in content.key_takeaways:
            st.markdown(f"- {point}")
    
    st.markdown("---")
    
    # 三级技能点列表
    micro_children = get_children(node.node_id)
    
    if micro_children:
        st.markdown(f"### 📚 技能点学习（共 {len(micro_children)} 个）")
        st.markdown("每个技能点至少包含1道练习题，完成题目即掌握该技能")
        
        for i, micro in enumerate(micro_children, 1):
            _render_micro_skill_card(micro, index=i)
    else:
        st.info("该知识点暂无下属技能点")
    
    # 前置知识点
    prereqs = get_prereqs(node.node_id, transitive=False)
    if prereqs:
        st.markdown("---")
        st.markdown("### 📋 前置知识")
        st.markdown("建议先掌握以下知识点再学习本节内容")
        cols = st.columns(min(3, len(prereqs)))
        for i, pre in enumerate(prereqs):
            with cols[i % 3]:
                color = LEVEL_COLORS.get(pre.level, "#6b7280")
                st.markdown(f"""
                <div style="background:{color}10;border-left:3px solid {color};padding:0.5rem;margin-bottom:0.5rem;border-radius:4px;">
                    <div style="font-size:0.9rem;color:#1f2937;font-weight:500;">{pre.name}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"查看", key=f"prereq_{pre.node_id}", use_container_width=True):
                    go_to_knowledge_detail(pre.node_id)
                    st.rerun()
    
    # AI 教师对话
    render_ai_teacher_chat(
        context_type="knowledge",
        context_id=node.node_id,
        context_data={
            "name": node.name,
            "level": node.level,
            "subject": node.subject,
            "summary": content.content_summary if content else "",
        },
        key_prefix="meso_",
    )


def _render_micro_skill_card(micro, index: int) -> None:
    """渲染三级技能点卡片"""
    color = LEVEL_COLORS["micro"]
    
    # 获取该技能点的关联题目
    items = get_items_for_node(micro.node_id)
    item_count = len(items)
    
    summary = micro.content.content_summary if micro.content else ""
    
    with st.expander(f"**{index}. {micro.name}** ({item_count} 道题目)", expanded=False):
        if summary:
            st.markdown(f"*{summary}*")
        
        if items:
            st.markdown(f"**练习题目** (共 {item_count} 道)")
            
            for item_id, domain in items[:3]:  # 最多显示3道
                if domain == "coding":
                    item = get_coding_item_by_id(item_id)
                elif domain == "math":
                    item = get_math_item_by_id(item_id)
                else:
                    item = get_dl_item_by_id(item_id)
                
                if not item:
                    continue
                
                domain_icon = {"coding": "💻", "math": "📐", "deeplearning": "🧠"}.get(domain, "📝")
                badge_class, badge_text = difficulty_to_badge(item.difficulty)
                
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"{domain_icon} **{item.title}** ({badge_text})")
                with col2:
                    if st.button("开始", key=f"micro_item_{micro.node_id}_{item_id}", use_container_width=True):
                        go_to_problem(domain, item_id)
                        st.rerun()
            
            if item_count > 3:
                st.caption(f"还有 {item_count - 3} 道题目...")
        else:
            st.info("该技能点暂无关联题目")


def _render_micro_detail(node) -> None:
    """渲染三级技能点详情"""
    content = node.content
    
    if content and content.content_summary:
        st.markdown("### 📝 技能描述")
        st.markdown(content.content_summary)
    
    # 常见错误
    if node.common_mistakes:
        st.markdown("### ⚠️ 常见错误")
        for mistake in node.common_mistakes:
            st.markdown(f"- {mistake}")
    
    st.markdown("---")
    
    # 关联题目
    st.markdown("### 📚 练习题目")
    items = get_items_for_node(node.node_id)
    
    if items:
        st.markdown(f"完成以下 **{len(items)}** 道题目即掌握此技能")
        
        for item_id, domain in items:
            if domain == "coding":
                item = get_coding_item_by_id(item_id)
            elif domain == "math":
                item = get_math_item_by_id(item_id)
            else:
                item = get_dl_item_by_id(item_id)
            
            if not item:
                continue
            
            domain_icon = {"coding": "💻", "math": "📐", "deeplearning": "🧠"}.get(domain, "📝")
            badge_class, badge_text = difficulty_to_badge(item.difficulty)
            
            st.markdown(f"""
            <div style="background:white;border:1px solid #e5e7eb;border-radius:8px;padding:0.75rem;margin-bottom:0.5rem;">
                <div style="font-weight:600;color:#1f2937;">{domain_icon} {item.title}</div>
                <div style="display:flex;gap:0.5rem;margin-top:0.5rem;">
                    <span style="background:#f3f4f6;color:#6b7280;padding:2px 8px;border-radius:4px;font-size:0.75rem;">{badge_text}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"开始练习", key=f"kd_item_{item_id}", use_container_width=True):
                go_to_problem(domain, item_id)
                st.rerun()
    else:
        st.info("该技能点暂无关联题目")
    
    # 所属知识点
    ancestors = get_ancestors(node.node_id)
    if ancestors:
        st.markdown("---")
        st.markdown("### 🔼 所属知识点")
        for anc in ancestors[:3]:
            icon = SUBJECT_ICONS.get(anc.subject, "📖")
            if st.button(f"{icon} {anc.name}", key=f"anc_{anc.node_id}", use_container_width=True):
                go_to_knowledge_detail(anc.node_id)
                st.rerun()
    
    # AI 教师对话
    content = node.content
    render_ai_teacher_chat(
        context_type="knowledge",
        context_id=node.node_id,
        context_data={
            "name": node.name,
            "level": node.level,
            "subject": node.subject,
            "summary": content.content_summary if content else "",
        },
        key_prefix="micro_",
    )


def _render_macro_detail(node) -> None:
    """渲染一级知识点详情"""
    content = node.content
    
    if content and content.content_summary:
        st.markdown("### 📝 领域概述")
        st.markdown(content.content_summary)
    
    st.markdown("---")
    
    # 下属二级知识点
    meso_children = get_children(node.node_id)
    
    if meso_children:
        st.markdown(f"### 📚 学习路线（共 {len(meso_children)} 个知识点）")
        
        cols = st.columns(min(3, len(meso_children)))
        for i, meso in enumerate(meso_children):
            with cols[i % 3]:
                color = LEVEL_COLORS["meso"]
                micro_count = len(get_children(meso.node_id))
                
                st.markdown(f"""
                <div style="background:white;border:1px solid #e5e7eb;border-radius:8px;padding:0.75rem;margin-bottom:0.5rem;border-left:3px solid {color};">
                    <div style="font-weight:600;color:{color};">{meso.name}</div>
                    <div style="font-size:0.75rem;color:#9ca3af;margin-top:0.25rem;">{micro_count} 个技能点</div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"开始学习", key=f"macro_meso_{meso.node_id}", use_container_width=True):
                    go_to_knowledge_detail(meso.node_id)
                    st.rerun()
    else:
        st.info("该领域暂无下属知识点")
    
    # AI 教师对话
    render_ai_teacher_chat(
        context_type="knowledge",
        context_id=node.node_id,
        context_data={
            "name": node.name,
            "level": node.level,
            "subject": node.subject,
            "summary": content.content_summary if content else "",
        },
        key_prefix="macro_",
    )
