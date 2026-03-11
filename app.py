
from __future__ import annotations

import streamlit as st

# 页面配置（必须在其他 Streamlit 调用之前）
st.set_page_config(
    page_title="Ascend Flow（智流）",
    page_icon="🚀",
    layout="wide",
)

# 导入前端模块
from frontend import (
    inject_global_css,
    inject_sidebar_js,
    topbar,
    init_state,
    render_sidebar,
    render_login,
    render_home,
    render_library,
    render_coding_problem,
    render_math_problem,
    render_dl_problem,
    render_knowledge_map,
    render_knowledge_detail,
)


def main() -> None:
    """应用主入口"""
    # 初始化
    init_state()

    # 注入样式
    inject_global_css()
    inject_sidebar_js()

    # 顶部栏（登录页也保持同风格）
    topbar()

    # 未登录：显示登录页（不渲染侧边栏/路由）
    if not st.session_state.get("logged_in"):
        render_login()
        return

    # 渲染侧边栏
    render_sidebar()
    
    # 路由：根据当前页面状态渲染对应内容
    _render_current_page()


def _render_current_page() -> None:
    """根据当前状态渲染页面"""
    page = st.session_state.page

    if page == "home":
        render_home()
    elif page == "library":
        render_library()
    elif page == "knowledge_map":
        render_knowledge_map()
    elif page == "knowledge_detail":
        render_knowledge_detail()
    elif page == "problem":
        _render_problem_page()
    else:
        render_home()


def _render_problem_page() -> None:
    """渲染题目页面"""
    ptype = st.session_state.current_problem_type

    if ptype == "coding":
        render_coding_problem()
    elif ptype == "math":
        render_math_problem()
    elif ptype == "deeplearning":
        render_dl_problem()


if __name__ == "__main__":
    main()
