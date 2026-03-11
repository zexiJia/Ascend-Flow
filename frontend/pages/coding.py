# filename: frontend/pages/coding.py
"""编程题页面渲染"""

from __future__ import annotations

import streamlit as st
from streamlit_ace import st_ace

from problems.coding.loader import get_coding_item_by_id
from problems.coding.evaluator import run_tests
from services.progress import problem_key, record_attempt, mark_completed, mark_checked
from services.ai_grader import AI_ENABLED, agent_grade_coding
from frontend.pages.common import render_ai_teacher_grade
from frontend.ui_utils import difficulty_to_badge
from frontend.pages._item_panels import render_item_knowledge_panel, render_similar_items_panel
from frontend.components.ai_chat import render_ai_teacher_chat


def render_coding_problem() -> None:
    """渲染编程题页面"""
    item = get_coding_item_by_id(st.session_state.current_problem_id)
    if not item:
        st.error("题目不存在")
        return

    # 标题和难度
    c1, c2 = st.columns([5, 1])
    with c1:
        st.markdown(f"## 💻 {item.title}")
    with c2:
        cls, label = difficulty_to_badge(item.difficulty)
        st.markdown(
            f'<span class="badge badge-{cls}">{label}</span>',
            unsafe_allow_html=True,
        )

    left, right = st.columns([1, 1], gap="large")

    # 左侧：题目描述
    with left:
        st.markdown("### 📋 题目描述")
        st.markdown(item.prompt)

        if getattr(item, "explanation", ""):
            with st.expander("📖 讲解 / 例题 / 应用", expanded=False):
                st.markdown(item.explanation)

        with st.expander("🧠 知识点", expanded=True):
            render_item_knowledge_panel(domain="coding", item_id=item.item_id, knowledge_links=item.knowledge_links)

        with st.expander("🧩 相似题推荐", expanded=False):
            render_similar_items_panel(domain="coding", item_id=item.item_id)

    # 右侧：代码编辑器
    with right:
        st.markdown("### ✏️ 代码编辑器")

        # Hints
        h1, h2, h3 = st.columns(3)
        with h1:
            if st.button("💡 Hint 1", key="hint_1", width="stretch"):
                st.session_state.show_hints = 1
        with h2:
            if st.button("💡 Hint 2", key="hint_2", width="stretch"):
                st.session_state.show_hints = 2
        with h3:
            if st.button("💡 Hint 3", key="hint_3", width="stretch"):
                st.session_state.show_hints = 3

        if st.session_state.show_hints > 0:
            st.warning(f"**Hint**: {item.hints.get(st.session_state.show_hints, '暂无')}")

        # 代码编辑器
        code = st_ace(
            value=st.session_state.user_code,
            language="python",
            theme="github",
            key=f"ace_{item.item_id}",
            height=300,
            font_size=14,
            tab_size=4,
            auto_update=True,
        )
        st.session_state.user_code = code if isinstance(code, str) else st.session_state.user_code

        tests = (item.grader or {}).get("tests", [])

        # 按钮行
        b1, b2, b3 = st.columns(3)

        with b1:
            if st.button("▶️ 运行测试", type="primary", width="stretch"):
                r = run_tests(
                    user_code=st.session_state.user_code,
                    func_name=item.function_name,
                    tests=tests,
                    timeout_s=2.0,
                ).to_json()
                st.session_state.coding_result = r

                record_attempt(
                    ptype="coding",
                    pid=item.item_id,
                    event="run_tests",
                    ok=bool(r.get("ok")),
                    meta={"passed": r.get("passed"), "total": r.get("total")},
                )

                if r.get("ok"):
                    mark_completed(ptype="coding", pid=item.item_id)
                    mark_checked(ptype="coding", pid=item.item_id, correct=True)

                st.rerun()

        with b2:
            if st.button("AI老师批改", width="stretch", disabled=(not AI_ENABLED)):
                with st.spinner("AI老师批改中..."):
                    # 直接调用 AI 批改，不需要先跑测试
                    text = agent_grade_coding(
                        problem=item,
                        user_code=st.session_state.user_code,
                        test_result=st.session_state.coding_result,  # 可能为 None
                    )
                    st.session_state.agent_grades[problem_key("coding", item.item_id)] = text

                record_attempt(ptype="coding", pid=item.item_id, event="agent_grade", ok=None)
                st.rerun()

        with b3:
            if st.button("🔄 重置", width="stretch"):
                st.session_state.user_code = item.starter_code
                st.session_state.coding_result = None
                st.rerun()

        # 显示测试结果
        if st.session_state.coding_result:
            r = st.session_state.coding_result
            if r.get("ok"):
                st.success(f"🎉 全部通过！{r.get('passed')}/{r.get('total')}")
            else:
                st.error(f"❌ {r.get('passed', 0)}/{r.get('total', 0)} 通过")
                if r.get("runtime_error"):
                    st.code(r["runtime_error"])

            cases = r.get("cases") or []
            if cases:
                st.markdown("### 🧪 测试用例详情")
                for i, c in enumerate(cases, 1):
                    name = c.get("name") or f"case_{i}"
                    passed = bool(c.get("passed"))
                    title = f"{'✅' if passed else '❌'} {name}"
                    with st.expander(title, expanded=(not passed)):
                        st.write(f"**结果**：{'通过' if passed else '未通过'}")
                        st.markdown("**输入 args**")
                        st.code(repr(c.get("args")), language="python")
                        st.markdown("**期望 expected**")
                        st.code(repr(c.get("expected")), language="python")
                        st.markdown("**实际 got**")
                        st.code(repr(c.get("got")), language="python")

                        out = (c.get("stdout") or "").strip()
                        if out:
                            st.markdown("**运行输出 stdout/stderr**")
                            st.code(out)

                        err = c.get("error")
                        if err:
                            st.markdown("**错误**")
                            st.code(str(err))
                        tb = c.get("traceback")
                        if tb:
                            st.markdown("**Traceback**")
                            st.code(str(tb))

        # AI 批改结果
        g = st.session_state.agent_grades.get(problem_key("coding", item.item_id))
        if g:
            render_ai_teacher_grade(title="AI老师批改", text=g)
    
    # AI 教师对话
    render_ai_teacher_chat(
        context_type="problem",
        context_id=item.item_id,
        context_data={
            "domain": "编程",
            "title": item.title,
            "prompt": item.prompt,
            "difficulty": item.difficulty,
            "explanation": getattr(item, "explanation", ""),
        },
        key_prefix="coding_",
    )
