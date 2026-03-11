# filename: frontend/state.py
"""状态管理 - Session state 初始化与管理"""
from __future__ import annotations

import streamlit as st


def init_state() -> None:
    """初始化所有 session state 变量"""
    defaults = {
        # 登录
        "logged_in": False,
        "current_user": None,
        "login_error": "",
        # 页面导航
        "page": "home",
        "library_category": None,
        "current_problem_type": None,
        "current_problem_id": None,
        # 知识图谱
        "current_knowledge_node_id": None,  # 当前查看的知识点
        "knowledge_map_subject": None,      # 知识地图筛选的学科
        "selected_kg_node": None,           # 知识图谱中选中的节点（用于显示信息卡片）
        # 每日精选
        "daily_knowledge": None,  # 今日知识点主线
        "daily_picks": None,      # 今日练习题目列表
        "daily_theme": "",
        "show_all_daily_picks": False,
        # 进度追踪
        "progress_by_date": {},
        "today_ai_summary": None,
        "today_ai_summary_date": None,
        # AI 批改结果
        "agent_grades": {},  # problem_key -> agent feedback text
        # Coding 题状态
        "user_code": "",
        "coding_result": None,
        # Math 题状态
        "user_math_answer": "",
        "math_selected_option": None,
        "math_selected_options": [],
        "math_fill_answers": {},
        "math_result": None,
        # DeepLearning 题状态
        "dl_selected_option": None,
        "dl_fill_answers": {},
        "dl_code": "",
        "dl_result": None,
        # 提示
        "show_hints": 0,
        # 历史记录查看
        "view_history_date": None,
        "show_full_history": False,
    }
    
    for key, default in defaults.items():
        st.session_state.setdefault(key, default)


def reset_problem_state() -> None:
    """重置题目相关状态（切换题目时调用）"""
    reset_keys = {
        "coding_result": None,
        "math_result": None,
        "dl_result": None,
        "dl_selected_option": None,
        "math_selected_option": None,
    }
    
    for key, value in reset_keys.items():
        st.session_state[key] = value
    
    st.session_state.dl_fill_answers = {}
    st.session_state.math_fill_answers = {}
    st.session_state.math_selected_options = []
    st.session_state.show_hints = 0


def go_to_problem(ptype: str, pid: str) -> None:
    """导航到指定题目"""
    from problems.coding.loader import get_coding_item_by_id
    from problems.deeplearning.loader import get_dl_item_by_id
    
    st.session_state.page = "problem"
    st.session_state.current_problem_type = ptype
    st.session_state.current_problem_id = pid
    reset_problem_state()
    
    if ptype == "coding":
        p = get_coding_item_by_id(pid)
        if p:
            st.session_state.user_code = p.starter_code
    elif ptype == "deeplearning":
        p = get_dl_item_by_id(pid)
        if p and p.problem_type == "code":
            st.session_state.dl_code = p.starter_code


def go_to_library(cat: str) -> None:
    """导航到题库页面"""
    st.session_state.page = "library"
    st.session_state.library_category = cat


def go_to_knowledge_map(subject: str = None) -> None:
    """导航到知识地图页面"""
    st.session_state.page = "knowledge_map"
    st.session_state.knowledge_map_subject = subject


def go_to_knowledge_detail(node_id: str) -> None:
    """导航到知识点详情页面"""
    st.session_state.page = "knowledge_detail"
    st.session_state.current_knowledge_node_id = node_id


def go_home() -> None:
    """返回首页"""
    st.session_state.page = "home"


def logout() -> None:
    """退出登录（仅清理登录态，不删除本地存档）"""
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.login_error = ""
    st.session_state.page = "home"
