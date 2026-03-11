"""登录页面"""
from __future__ import annotations

import streamlit as st

from services.user_store import authenticate, load_user_progress


def render_login() -> None:
    """渲染登录界面（当前仅支持测试账号）"""
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.markdown(
        """
<div class="card" style="max-width:560px;margin:0 auto;">
  <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:10px;">
    <div>
      <div style="font-size:1.35rem;font-weight:800;margin-bottom:2px;">🔐 登录</div>
      <div style="color:#64748b;font-size:0.92rem;">当前仅开放测试账号</div>
    </div>
    <div style="color:#94a3b8;font-size:0.85rem;">Ascend Flow</div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            username = st.text_input("用户名", value="test", key="login_username")
            password = st.text_input("密码", type="password", key="login_password")

            if st.session_state.get("login_error"):
                st.error(st.session_state.login_error)

            if st.button("登录", width="stretch"):
                if authenticate(username.strip(), password):
                    st.session_state.logged_in = True
                    st.session_state.current_user = username.strip()
                    st.session_state.login_error = ""

                    # 加载历史进度
                    st.session_state.progress_by_date = load_user_progress(username.strip())

                    st.rerun()
                else:
                    st.session_state.login_error = "用户名或密码错误"
                    st.rerun()

            st.caption("测试账号：test / 123123")


