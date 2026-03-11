# filename: frontend/sidebar.py
"""侧边栏渲染"""

from __future__ import annotations

import streamlit as st

from problems.coding.loader import get_coding_items, get_coding_item_by_id
from problems.math.loader import get_math_items, get_math_item_by_id
from problems.deeplearning.loader import get_dl_items, get_dl_item_by_id

from knowledge.loader import get_knowledge_nodes_by_level
from services.daily import generate_daily_selection
from frontend.state import go_to_problem, go_to_library, go_home, go_to_knowledge_map, go_to_knowledge_detail


def _simplify_title(title: str, max_len: int = 18) -> str:
    """简化题目标题，用于侧边栏显示
    - 取冒号前的部分（避免数学公式）
    - 限制最大长度
    """
    # 尝试取冒号前的部分
    for sep in ["：", ":"]:
        if sep in title:
            title = title.split(sep)[0].strip()
            break
    
    # 限制长度
    if len(title) > max_len:
        title = title[:max_len - 1] + "…"
    
    return title


def render_sidebar() -> None:
    """渲染侧边栏"""
    with st.sidebar:
        # Logo (点击返回首页)
        if st.button("🚀 智流", key="logo_home", width="stretch"):
            go_home()
            st.rerun()
        st.markdown("")

        _render_daily_picks()
        st.markdown("")

        _render_knowledge_library()
        st.markdown("")

        _render_problem_library()


def _render_daily_picks() -> None:
    """渲染今日练习区域 - 默认显示3题，可展开全部"""
    from services.progress import get_today_progress, problem_key
    from services.daily import generate_daily_knowledge, knowledge_to_dict
    
    # 确保数据初始化（与首页一致）
    if st.session_state.daily_knowledge is None:
        knowledge_nodes = generate_daily_knowledge(count=3)
        st.session_state.daily_knowledge = [knowledge_to_dict(k) for k in knowledge_nodes]
        picks, theme = generate_daily_selection(knowledge_nodes)
        st.session_state.daily_picks = picks
        st.session_state.daily_theme = theme

    picks = st.session_state.daily_picks or []
    prog = get_today_progress()
    total = len(picks)
    completed = sum(1 for p in picks if prog["completed"].get(problem_key(p["type"], p["id"])))

    st.markdown(f"**📅 今日练习** ({completed}/{total})")

    if not picks:
        st.caption("暂无今日练习")
        return

    # 是否展开全部
    show_all = st.session_state.get("sidebar_show_all_picks", False)
    display_picks = picks if show_all else picks[:3]

    for pick in display_picks:
        icon = {"coding": "💻", "math": "📐", "deeplearning": "🧠"}.get(pick["type"], "📝")
        k = problem_key(pick["type"], pick["id"])
        done = bool(prog["completed"].get(k))

        if pick["type"] == "coding":
            p = get_coding_item_by_id(pick["id"])
        elif pick["type"] == "math":
            p = get_math_item_by_id(pick["id"])
        else:
            p = get_dl_item_by_id(pick["id"])

        title = p.title if p else "练习题目"
        # 简化标题：取冒号前的部分，避免数学公式显示混乱
        display_title = _simplify_title(title)
        status = "✅" if done else "○"

        if st.button(f"{status} {icon} {display_title}", key=f"daily_{pick['id']}", width="stretch"):
            go_to_problem(pick["type"], pick["id"])
            st.rerun()

    # 展开/收起按钮（放在题目下方）
    if len(picks) > 3:
        remaining = len(picks) - 3
        if not show_all:
            if st.button(f"查看全部 ({remaining}题)", key="sb_expand_picks", width="stretch"):
                st.session_state.sidebar_show_all_picks = True
                st.rerun()
        else:
            if st.button("收起", key="sb_collapse_picks", width="stretch"):
                st.session_state.sidebar_show_all_picks = False
                st.rerun()


def _render_knowledge_library() -> None:
    """渲染知识库入口 - 类似题库的结构"""
    from knowledge.loader import get_all_knowledge_nodes
    
    with st.expander("📖 **知识库**", expanded=False):
        all_nodes = get_all_knowledge_nodes()
        
        # 按学科分组
        by_subject = {"math": [], "coding": [], "deeplearning": []}
        for node in all_nodes:
            if node.level in ("macro", "meso") and node.subject in by_subject:
                by_subject[node.subject].append(node)
        
        # 数学知识点
        st.caption("📐 数学")
        math_nodes = by_subject.get("math", [])
        for node in math_nodes[:2]:
            level_icon = "🔷" if node.level == "macro" else "🔹"
            if st.button(f"{level_icon} {node.name}", key=f"sb_kn_{node.node_id}", width="stretch"):
                go_to_knowledge_detail(node.node_id)
                st.rerun()
        if len(math_nodes) > 2:
            if st.button(f"📂 全部数学知识 ({len(math_nodes)})", key="more_math_kn", width="stretch"):
                go_to_knowledge_map("math")
                st.rerun()

        st.markdown("---")
        
        # 编程知识点
        st.caption("💻 编程")
        coding_nodes = by_subject.get("coding", [])
        for node in coding_nodes[:2]:
            level_icon = "🔷" if node.level == "macro" else "🔹"
            if st.button(f"{level_icon} {node.name}", key=f"sb_kn_{node.node_id}", width="stretch"):
                go_to_knowledge_detail(node.node_id)
                st.rerun()
        if len(coding_nodes) > 2:
            if st.button(f"📂 全部编程知识 ({len(coding_nodes)})", key="more_coding_kn", width="stretch"):
                go_to_knowledge_map("coding")
                st.rerun()

        st.markdown("---")
        
        # 深度学习知识点
        st.caption("🧠 深度学习")
        dl_nodes = by_subject.get("deeplearning", [])
        for node in dl_nodes[:2]:
            level_icon = "🔷" if node.level == "macro" else "🔹"
            if st.button(f"{level_icon} {node.name}", key=f"sb_kn_{node.node_id}", width="stretch"):
                go_to_knowledge_detail(node.node_id)
                st.rerun()
        if len(dl_nodes) > 2:
            if st.button(f"📂 全部深度学习知识 ({len(dl_nodes)})", key="more_dl_kn", width="stretch"):
                go_to_knowledge_map("deeplearning")
                st.rerun()

        st.markdown("---")
        
        # 知识图谱入口
        if st.button("🗺️ 查看知识图谱", key="view_knowledge_map", width="stretch"):
            go_to_knowledge_map()
            st.rerun()


def _render_problem_library() -> None:
    """渲染题库列表"""
    with st.expander("📚 **题库**", expanded=False):
        st.caption("💻 编程题")
        coding_items = get_coding_items()
        for p in coding_items[:5]:
            if st.button(f"{p.title}", key=f"sb_c_{p.item_id}", width="stretch"):
                go_to_problem("coding", p.item_id)
                st.rerun()
        if len(coding_items) > 5:
            if st.button(f"📂 全部编程题 ({len(coding_items)})", key="more_coding", width="stretch"):
                go_to_library("coding")
                st.rerun()

        st.markdown("---")

        st.caption("📐 数学题")
        math_items = get_math_items()
        for p in math_items[:5]:
            if st.button(f"{p.title}", key=f"sb_m_{p.item_id}", width="stretch"):
                go_to_problem("math", p.item_id)
                st.rerun()
        if len(math_items) > 5:
            if st.button(f"📂 全部数学题 ({len(math_items)})", key="more_math", width="stretch"):
                go_to_library("math")
                st.rerun()

        st.markdown("---")

        st.caption("🧠 深度学习题")
        dl_items = get_dl_items()
        for p in dl_items[:5]:
            if st.button(f"{p.title}", key=f"sb_dl_{p.item_id}", width="stretch"):
                go_to_problem("deeplearning", p.item_id)
                st.rerun()
        if len(dl_items) > 5:
            if st.button(f"📂 全部深度学习题 ({len(dl_items)})", key="more_dl", width="stretch"):
                go_to_library("deeplearning")
                st.rerun()
