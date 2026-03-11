# filename: frontend/theme.py
"""全局 CSS 和主题注入"""
from __future__ import annotations

import streamlit as st


def inject_global_css() -> None:
    """注入全局 CSS 样式"""
    st.markdown(
        """
        <style>
        /* ===== 隐藏 Streamlit Deploy 按钮（use_container_width 迁移提示关联的 UI）===== */
        button[data-testid="stDeployButton"],
        div[data-testid="stToolbarActions"] button[title="Deploy"],
        div[data-testid="stToolbarActions"] a[title="Deploy"] {
            display: none !important;
        }

        /* ===== 全局背景 ===== */
        .stApp { 
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%); 
        }

        /* ===== 顶部品牌栏 ===== */
        .af-topbar { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            padding: 1rem 2rem; 
            border-radius: 16px; 
            margin-bottom: 1.5rem; 
            color: white; 
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3); 
        }
        .af-topbar-inner{
            display:flex;
            align-items:center;
            justify-content:space-between;
            gap:16px;
        }
        .af-topbar-left{
            display:flex;
            flex-direction:column;
        }
        .af-topbar h1 { 
            margin: 0; 
            font-size: 1.6rem; 
            font-weight: 800; 
        }
        .af-topbar p { 
            margin: 0.2rem 0 0 0; 
            opacity: 0.9; 
            font-size: 0.9rem; 
        }
        .af-user{
            display:flex;
            align-items:center;
            gap:10px;
            padding: 8px 10px;
            border-radius: 999px;
            background: rgba(255,255,255,0.14);
            border: 1px solid rgba(255,255,255,0.22);
        }
        .af-avatar{
            width:34px;
            height:34px;
            border-radius:50%;
            display:flex;
            align-items:center;
            justify-content:center;
            font-weight:800;
            color:white;
            background: rgba(255,255,255,0.22);
            flex-shrink:0;
        }
        .af-user-meta{
            display:flex;
            flex-direction:column;
            line-height:1.1;
            min-width: 80px;
        }
        .af-user-name{
            font-weight:750;
            font-size:0.92rem;
            opacity: 0.98;
        }
        .af-user-sub{
            font-size:0.78rem;
            opacity:0.86;
        }

        /* ===== 卡片组件 ===== */
        .card { 
            background: white; 
            border: 1px solid rgba(0,0,0,0.06); 
            border-radius: 16px; 
            padding: 1.25rem; 
            margin-bottom: 1rem; 
            box-shadow: 0 4px 20px rgba(0,0,0,0.04); 
            transition: all 0.2s ease; 
        }
        .card:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 8px 30px rgba(0,0,0,0.08); 
        }

        /* ===== 课程卡片 ===== */
        .lesson-card { 
            cursor: pointer; 
            transition: all 0.3s ease; 
        }
        .lesson-card:hover { 
            transform: translateY(-4px); 
            box-shadow: 0 12px 40px rgba(102, 126, 234, 0.15); 
        }

        /* ===== 徽章 ===== */
        .badge { 
            display: inline-block; 
            padding: 0.3rem 0.8rem; 
            border-radius: 20px; 
            font-size: 0.75rem; 
            font-weight: 700; 
        }
        .badge-easy { 
            background: #d1fae5; 
            color: #065f46; 
        }
        .badge-medium { 
            background: #fef3c7; 
            color: #92400e; 
        }
        .badge-hard { 
            background: #fee2e2; 
            color: #991b1b; 
        }

        /* ===== 首页 Hero ===== */
        .home-hero { 
            text-align: center; 
            padding: 2rem; 
            background: white; 
            border-radius: 20px; 
            margin: 1rem 0; 
            box-shadow: 0 4px 20px rgba(0,0,0,0.04); 
        }

        /* ===== AI 批改卡片 ===== */
        .ai-card {
            background: white;
            border: 1px solid rgba(102, 126, 234, 0.2);
            border-radius: 12px;
            padding: 1rem;
            margin-top: 1rem;
            box-shadow: 0 4px 16px rgba(102, 126, 234, 0.1);
        }

        /* ===== 侧边栏样式 ===== */
        section[data-testid="stSidebar"] { 
            background: white; 
        }

        /* 侧边栏按钮 */
        section[data-testid="stSidebar"] .stButton > button {
            background: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            color: #334155 !important;
            text-align: left !important;
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            border-radius: 10px !important;
            padding: 0.55rem 0.75rem !important;
            box-shadow: none !important;
        }
        section[data-testid="stSidebar"] .stButton > button:hover {
            background: #f8fafc !important;
            border-color: #cbd5e1 !important;
        }

        /* ===== 通用样式 ===== */
        .af-muted { 
            color: rgba(27,36,48,0.68); 
        }
        .af-mono { 
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; 
        }

        /* ===== 高级卡片 ===== */
        .af-card {
            padding: 16px 16px;
            border-radius: 16px;
            border: 1px solid rgba(17,24,39,0.08);
            background: #ffffff;
            box-shadow: 0 10px 28px rgba(16,24,40,0.06);
            transition: transform 140ms ease, box-shadow 140ms ease;
        }
        .af-card:hover { 
            transform: translateY(-1px); 
            box-shadow: 0 14px 34px rgba(16,24,40,0.08); 
        }
        .af-card-title { 
            font-weight: 760; 
            font-size: 16px; 
            margin-bottom: 4px; 
        }
        .af-card-row { 
            display: flex; 
            gap: 10px; 
            flex-wrap: wrap; 
            margin-top: 10px; 
        }
        .af-chip {
            display: inline-flex; 
            align-items: center; 
            gap: 6px;
            padding: 6px 10px; 
            border-radius: 999px;
            border: 1px solid rgba(17,24,39,0.10);
            background: rgba(17,24,39,0.03);
            font-size: 12.5px;
            color: rgba(27,36,48,0.82);
        }

        /* ===== 状态徽章 ===== */
        .af-badge { 
            display: inline-flex; 
            align-items: center; 
            gap: 8px; 
            padding: 6px 10px; 
            border-radius: 999px; 
            font-size: 12.5px; 
            font-weight: 650; 
        }
        .af-badge-done { 
            background: rgba(16,185,129,0.12); 
            color: rgb(5,122,85); 
            border: 1px solid rgba(16,185,129,0.22); 
        }
        .af-badge-now  { 
            background: rgba(91,124,250,0.12); 
            color: rgb(54,83,210); 
            border: 1px solid rgba(91,124,250,0.24); 
        }
        .af-badge-next { 
            background: rgba(245,158,11,0.12); 
            color: rgb(161,98,7); 
            border: 1px solid rgba(245,158,11,0.22); 
        }

        /* ===== Stepper 组件 ===== */
        .af-stepper { 
            display: flex; 
            align-items: stretch; 
            gap: 10px; 
            flex-wrap: wrap; 
            margin: 10px 0 12px; 
        }
        .af-step {
            flex: 1 1 180px;
            border-radius: 14px;
            border: 1px solid rgba(17,24,39,0.08);
            background: #fff;
            padding: 10px 12px;
            box-shadow: 0 8px 20px rgba(16,24,40,0.05);
        }
        .af-step-title { 
            font-weight: 740; 
            font-size: 13.5px; 
        }
        .af-step-sub { 
            margin-top: 3px; 
            font-size: 12px; 
            color: rgba(27,36,48,0.65); 
        }

        /* ===== Streamlit 组件微调 ===== */
        div.stButton > button {
            border-radius: 12px !important;
            height: 44px !important;
            font-weight: 650 !important;
        }
        div[data-testid="stChatMessage"] { 
            border-radius: 16px; 
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def inject_sidebar_js() -> None:
    """注入侧边栏按钮样式的 JavaScript"""
    st.markdown(
        """
        <script>
        // 为智流 Logo 按钮添加特殊样式
        const observer = new MutationObserver(() => {
            const buttons = document.querySelectorAll('section[data-testid="stSidebar"] button');
            buttons.forEach(btn => {
                const text = (btn.textContent || '').trim();
                
                // 智流：深色渐变
                if (text.includes('智流')) {
                    btn.style.setProperty('background', 'linear-gradient(135deg, #0f172a 0%, #312e81 60%, #581c87 100%)', 'important');
                    btn.style.setProperty('color', '#ffffff', 'important');
                    btn.style.fontSize = '1.2rem';
                    btn.style.fontWeight = '700';
                    btn.style.border = 'none';
                    btn.style.borderRadius = '12px';
                    btn.style.padding = '0.8rem';
                    btn.style.textAlign = 'center';
                    btn.style.setProperty('box-shadow', '0 6px 18px rgba(15, 23, 42, 0.25)', 'important');
                    return;
                }

                // Coding 按钮
                if (text.startsWith('💻')) {
                    btn.style.setProperty('background', 'linear-gradient(135deg, #dbeafe 0%, #e0e7ff 100%)', 'important');
                    btn.style.setProperty('color', '#0f172a', 'important');
                    btn.style.setProperty('box-shadow', '0 4px 14px rgba(37, 99, 235, 0.14)', 'important');
                    return;
                }
                
                // Math 按钮
                if (text.startsWith('📐')) {
                    btn.style.setProperty('background', 'linear-gradient(135deg, #dcfce7 0%, #d1fae5 100%)', 'important');
                    btn.style.setProperty('color', '#0f172a', 'important');
                    btn.style.setProperty('box-shadow', '0 4px 14px rgba(34, 197, 94, 0.14)', 'important');
                    return;
                }
                
                // DeepLearning 按钮
                if (text.startsWith('🧠')) {
                    btn.style.setProperty('background', 'linear-gradient(135deg, #fce7f3 0%, #ede9fe 100%)', 'important');
                    btn.style.setProperty('color', '#0f172a', 'important');
                    btn.style.setProperty('box-shadow', '0 4px 14px rgba(168, 85, 247, 0.14)', 'important');
                    return;
                }
            });
        });
        observer.observe(document.body, { childList: true, subtree: true });
        </script>
        """,
        unsafe_allow_html=True,
    )


def topbar() -> None:
    """渲染顶部品牌栏"""
    user = st.session_state.get("current_user") or "未登录"
    logged_in = bool(st.session_state.get("logged_in"))
    sub = "已登录" if logged_in else "请登录"
    # 头像：优先取用户名首字符（中文/英文都可）
    initial = (user[:1] or "U").upper()
    st.markdown(
        f"""
        <div class="af-topbar">
          <div class="af-topbar-inner">
            <div class="af-topbar-left">
              <h1>🚀 Ascend Flow / 智流</h1>
              <p>题库 · 每日精选 · 学习私教</p>
            </div>
            <div class="af-user">
              <div class="af-avatar">{initial}</div>
              <div class="af-user-meta">
                <div class="af-user-name">{user}</div>
                <div class="af-user-sub">{sub}</div>
              </div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
