# filename: frontend/pages/home.py
"""首页渲染 - 简洁美观设计"""
from __future__ import annotations

from datetime import datetime

import streamlit as st

from problems.coding.loader import get_coding_item_by_id
from problems.math.loader import get_math_item_by_id
from problems.deeplearning.loader import get_dl_item_by_id
from services.progress import (
    today_key, get_today_progress, problem_key,
    get_all_progress_dates, get_date_summary,
)
from services.ai_grader import AI_ENABLED, ai_today_summary
from services.daily import generate_daily_knowledge, generate_daily_selection, knowledge_to_dict
from frontend.state import go_to_problem, go_to_knowledge_detail, go_to_knowledge_map


def render_home() -> None:
    """渲染首页"""
    # 初始化数据
    _init_daily_content()

    # Hero 区域
    _render_hero()
    
    # 主内容区：知识点(左) + 练习&历史(右)
    _render_main_content()
    
    # 底部统计
    _render_footer_stats()


def _init_daily_content() -> None:
    """初始化今日知识点和练习"""
    if st.session_state.daily_knowledge is None:
        knowledge_nodes = generate_daily_knowledge(count=3)
        st.session_state.daily_knowledge = [knowledge_to_dict(k) for k in knowledge_nodes]
        picks, theme = generate_daily_selection(knowledge_nodes)
        st.session_state.daily_picks = picks
        st.session_state.daily_theme = theme


def _render_hero() -> None:
    """渲染 Hero 区域"""
    now = datetime.now()
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    weekday = weekdays[now.weekday()]
    month_day = now.strftime("%m.%d")
    
    # 获取进度
    prog = get_today_progress()
    picks = st.session_state.daily_picks or []
    pick_keys = [problem_key(p["type"], p["id"]) for p in picks]
    completed = sum(1 for k in pick_keys if prog["completed"].get(k))
    total = len(picks)
    
    st.markdown(
        f'''<div style="background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:20px;padding:2rem;color:white;margin-bottom:2rem;box-shadow:0 4px 20px rgba(99,102,241,0.3);">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <p style="margin:0;font-size:0.9rem;opacity:0.8;">{weekday}</p>
                    <h1 style="margin:0.25rem 0;font-size:2.5rem;font-weight:700;">{month_day}</h1>
                    <p style="margin:0;font-size:1rem;opacity:0.9;">今日学习进度</p>
                </div>
                <div style="text-align:center;background:rgba(255,255,255,0.15);border-radius:16px;padding:1.25rem 2rem;backdrop-filter:blur(10px);">
                    <div style="font-size:2.5rem;font-weight:700;">{completed}<span style="font-size:1.2rem;opacity:0.7;">/{total}</span></div>
                    <div style="font-size:0.85rem;opacity:0.8;">题目完成</div>
                </div>
            </div>
        </div>''',
        unsafe_allow_html=True,
    )
    

def _render_main_content() -> None:
    """渲染主内容区 - 2x2 网格布局"""
    col1, col2 = st.columns(2, gap="medium")
    
    with col1:
        _render_knowledge_card()
    with col2:
        _render_practice_card()
    
    col3, col4 = st.columns(2, gap="medium")
    
    with col3:
        _render_map_card()
    with col4:
        _render_history_card()


def _render_card_header(icon: str, title: str, badge: str, colors: dict) -> None:
    """渲染统一的卡片头部"""
    st.markdown(
        f'''<div style="background:linear-gradient(135deg,{colors['bg1']},{colors['bg2']});
            border-radius:12px;padding:1rem;margin-bottom:0.5rem;border:1px solid {colors['border']};">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:1rem;font-weight:600;color:{colors['text']};">{icon} {title}</span>
                <span style="background:{colors['badge']};color:white;padding:3px 10px;
                    border-radius:12px;font-size:0.75rem;">{badge}</span>
            </div>
        </div>''',
        unsafe_allow_html=True,
    )
    

def _render_knowledge_card() -> None:
    """今日知识卡片 - 绿色"""
    knowledge_list = st.session_state.daily_knowledge or []
    colors = {"bg1": "#ecfdf5", "bg2": "#d1fae5", "border": "#a7f3d0", 
              "text": "#065f46", "badge": "#10b981"}
    
    _render_card_header("🎯", "今日知识", f"{len(knowledge_list)}个", colors)
    
    for kn in knowledge_list:
        icon = kn.get("icon", "📖")
        name = kn.get("name", "")
        node_id = kn.get("node_id", "")
        if st.button(f"{icon} {name}", key=f"kn_{node_id}", use_container_width=True):
            go_to_knowledge_detail(node_id)
            st.rerun()


def _render_practice_card() -> None:
    """今日练习卡片 - 紫色"""
    picks = st.session_state.daily_picks or []
    prog = get_today_progress()
    total = len(picks)
    pick_keys = [problem_key(p["type"], p["id"]) for p in picks]
    completed = sum(1 for k in pick_keys if prog["completed"].get(k))
    
    colors = {"bg1": "#f5f3ff", "bg2": "#ede9fe", "border": "#c4b5fd",
              "text": "#5b21b6", "badge": "#8b5cf6"}
    
    _render_card_header("📝", "今日练习", f"{completed}/{total}", colors)
    
    show_all = st.session_state.get("show_all_picks", False)
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
        
        title = p.title if p else pick["id"]
        for sep in ["：", ":"]:
            if sep in title:
                title = title.split(sep)[0].strip()
                break
        if len(title) > 12:
            title = title[:11] + "…"
        
        status = "✅" if done else "○"
        if st.button(f"{status} {icon} {title}", key=f"pick_{pick['id']}", use_container_width=True):
            go_to_problem(pick["type"], pick["id"])
            st.rerun()
    
    if len(picks) > 3:
        remaining = len(picks) - 3
        if not show_all:
            if st.button(f"更多 +{remaining}", key="expand_picks", use_container_width=True):
                st.session_state.show_all_picks = True
                st.rerun()
        else:
            if st.button("收起", key="collapse_picks", use_container_width=True):
                st.session_state.show_all_picks = False
            st.rerun()
    

def _render_map_card() -> None:
    """知识图谱卡片 - 橙色"""
    colors = {"bg1": "#fff7ed", "bg2": "#ffedd5", "border": "#fed7aa",
              "text": "#9a3412", "badge": "#f97316"}
    
    _render_card_header("🗺️", "知识图谱", "探索", colors)
    
    st.markdown(
        '''<div style="font-size:0.85rem;color:#9a3412;margin:0.5rem 0;min-height:2.5rem;">
        可视化知识结构<br/>探索学习路径
        </div>''',
        unsafe_allow_html=True,
    )
    
    if st.button("🌊 探索知识海洋", key="map_explore", use_container_width=True, type="primary"):
        go_to_knowledge_map()
        st.rerun()


def _render_history_card() -> None:
    """学习记录卡片 - 蓝色"""
    all_dates = get_all_progress_dates()
    colors = {"bg1": "#eff6ff", "bg2": "#dbeafe", "border": "#93c5fd",
              "text": "#1e40af", "badge": "#3b82f6"}
    
    _render_card_header("📊", "学习记录", f"{len(all_dates)}天", colors)
    
    # 显示今日概况
    today = today_key()
    today_summary = get_date_summary(today)
    total_problems = sum(get_date_summary(d)["completed"] for d in all_dates) if all_dates else 0
    
    st.markdown(
        f'''<div style="font-size:0.85rem;color:#1e40af;margin:0.5rem 0;min-height:2.5rem;">
        今日 <b>{today_summary["completed"]}</b> 题 · {today_summary["accuracy"]*100:.0f}%<br/>
        累计 <b>{total_problems}</b> 题
        </div>''',
        unsafe_allow_html=True,
    )

    if st.button("📋 查看历史记录", key="view_history", use_container_width=True, type="primary"):
        st.session_state.show_history_modal = True
        st.rerun()
    
    # 历史记录弹窗
    if st.session_state.get("show_history_modal", False):
        _render_history_modal(all_dates)


def _render_history_modal(all_dates: list) -> None:
    """渲染历史记录详情"""
    with st.expander("📊 历史学习记录", expanded=True):
        if not all_dates:
            st.info("暂无学习记录")
        else:
            for date_key in all_dates[:10]:
                summary = get_date_summary(date_key)
                is_today = date_key == today_key()
                
                try:
                    dt = datetime.strptime(date_key, "%Y-%m-%d")
                    date_label = "今天" if is_today else dt.strftime("%m/%d %a")
                except:
                    date_label = date_key
                
                if summary["completed"] == 0:
                    status = "○"
                elif summary["accuracy"] >= 0.8:
                    status = "🟢"
                elif summary["accuracy"] >= 0.5:
                    status = "🟡"
                else:
                    status = "🔴"
                
                acc_pct = summary['accuracy'] * 100
                st.markdown(
                    f"{status} **{date_label}** · {summary['completed']}题 · {acc_pct:.0f}%"
                )
        
        if st.button("关闭", key="close_history_modal", use_container_width=True):
            st.session_state.show_history_modal = False
            st.rerun()


def _render_date_detail(date_key: str, summary: dict) -> None:
    """渲染某一天的学习详情"""
    try:
        dt = datetime.strptime(date_key, "%Y-%m-%d")
        date_str = dt.strftime("%Y年%m月%d日")
    except:
        date_str = date_key
    
    st.markdown(
        f'''<div style="background:linear-gradient(135deg,#fefce8,#fef9c3);border:1px solid #fde047;border-radius:12px;padding:1rem;margin:-0.25rem 0 0.75rem 0;">
            <h4 style="margin:0 0 0.75rem 0;font-size:1rem;color:#854d0e;">📅 {date_str} 学习总结</h4>
            <div style="display:flex;gap:1rem;margin-bottom:0.75rem;">
                <div style="flex:1;text-align:center;background:white;border-radius:8px;padding:0.5rem;">
                    <div style="font-size:1.2rem;font-weight:600;color:#8b5cf6;">{summary['completed']}</div>
                    <div style="font-size:0.75rem;color:#64748b;">完成题目</div>
                </div>
                <div style="flex:1;text-align:center;background:white;border-radius:8px;padding:0.5rem;">
                    <div style="font-size:1.2rem;font-weight:600;color:#10b981;">{summary['accuracy']*100:.0f}%</div>
                    <div style="font-size:0.75rem;color:#64748b;">正确率</div>
                </div>
                <div style="flex:1;text-align:center;background:white;border-radius:8px;padding:0.5rem;">
                    <div style="font-size:1.2rem;font-weight:600;color:#f59e0b;">{summary['attempts']}</div>
                    <div style="font-size:0.75rem;color:#64748b;">尝试次数</div>
                </div>
                        </div>
                    </div>''',
                    unsafe_allow_html=True,
                )
                
    # 评价
    if summary['completed'] == 0:
        comment = "😴 这天没有学习记录"
    elif summary['accuracy'] >= 0.8:
        comment = "🎉 表现优秀！继续保持！"
    elif summary['accuracy'] >= 0.5:
        comment = "👍 还不错，继续努力！"
    else:
        comment = "💪 需要多加练习，加油！"
    
    st.markdown(f"<p style='text-align:center;color:#64748b;font-size:0.85rem;margin:0;'>{comment}</p>", unsafe_allow_html=True)


def _render_footer_stats() -> None:
    """渲染底部统计 - 各自主题色渐变"""
    prog = get_today_progress()
    picks = st.session_state.daily_picks or []
    pick_keys = [problem_key(p["type"], p["id"]) for p in picks]

    checked = sum(1 for k in pick_keys if prog["checked"].get(k))
    correct = sum(1 for k in pick_keys if prog["checked"].get(k) and prog["correct"].get(k))
    acc = (correct / checked * 100) if checked else 0

    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    stats = [
        ("已判题", checked, "linear-gradient(135deg,#f5f3ff,#ede9fe)", "#8b5cf6", "#c4b5fd"),
        ("正确", correct, "linear-gradient(135deg,#ecfdf5,#d1fae5)", "#10b981", "#a7f3d0"),
        ("正确率", f"{acc:.0f}%", "linear-gradient(135deg,#fffbeb,#fef3c7)", "#f59e0b", "#fcd34d"),
    ]
    
    for col, (label, value, bg, color, border) in zip(cols, stats):
        with col:
            st.markdown(
                    f'''<div style="background:{bg};border:1px solid {border};border-radius:12px;padding:1rem;text-align:center;">
                        <div style="font-size:1.5rem;font-weight:600;color:{color};">{value}</div>
                        <div style="font-size:0.8rem;color:#64748b;">{label}</div>
                    </div>''',
                unsafe_allow_html=True,
            )

    # AI 总结入口
    if AI_ENABLED:
        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
        with st.expander("🤖 AI 学习总结", expanded=False):
            _render_ai_summary()


def _render_ai_summary() -> None:
    """渲染 AI 总结"""
    if st.session_state.today_ai_summary and st.session_state.today_ai_summary_date == today_key():
        st.markdown(st.session_state.today_ai_summary)
        if st.button("🔄 重新生成", key="regen"):
            st.session_state.today_ai_summary = None
            st.rerun()
    else:
        if st.button("✨ 生成总结", key="gen_summary", use_container_width=True):
            prog = get_today_progress()
            picks = st.session_state.daily_picks or []
            pick_keys = [problem_key(p["type"], p["id"]) for p in picks]

            completed = sum(1 for k in pick_keys if prog["completed"].get(k))
            checked = sum(1 for k in pick_keys if prog["checked"].get(k))
            correct = sum(1 for k in pick_keys if prog["checked"].get(k) and prog["correct"].get(k))
            acc = (correct / checked) if checked else 0.0

            knowledge_list = st.session_state.daily_knowledge or []
            kn_names = [k.get("name", "") for k in knowledge_list]

            prompt = (
                "你是学习教练，请简短总结今日学习情况。全部使用中文。\n\n"
                f"知识点：{', '.join(kn_names)}\n"
                f"完成：{completed}/{len(pick_keys)}，正确率：{acc*100:.0f}%\n"
            )

            with st.spinner("生成中..."):
                st.session_state.today_ai_summary = ai_today_summary(prompt)
                st.session_state.today_ai_summary_date = today_key()
            st.rerun()
