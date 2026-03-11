# filename: frontend/pages/deeplearning.py
"""深度学习题页面渲染"""

from __future__ import annotations

import streamlit as st
from streamlit_ace import st_ace

from problems.deeplearning.loader import get_dl_item_by_id
from problems.coding.evaluator import run_tests
from services.progress import problem_key, record_attempt, mark_completed, mark_checked
from services.ai_grader import AI_ENABLED, agent_grade_dl
from frontend.pages.common import render_ai_teacher_grade
from frontend.ui_utils import difficulty_to_badge
from frontend.pages._item_panels import render_item_knowledge_panel, render_similar_items_panel
from frontend.components.ai_chat import render_ai_teacher_chat


# 题型中文名
PROBLEM_TYPE_NAMES = {
    "choice": "选择题",
    "fill": "填空题",
    "code": "代码题",
}


def render_dl_problem() -> None:
    """渲染深度学习题页面"""
    item = get_dl_item_by_id(st.session_state.current_problem_id)
    if not item:
        st.error("题目不存在")
        return

    cls, label = difficulty_to_badge(item.difficulty)

    st.markdown(f"## 🧠 {item.title}")
    st.markdown(
        f'<span class="badge badge-{cls}">{label}</span>',
        unsafe_allow_html=True,
    )

    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown("### 📋 题目")
        st.markdown(item.prompt)

        with st.expander("🧠 知识点", expanded=True):
            render_item_knowledge_panel(domain="deeplearning", item_id=item.item_id, knowledge_links=item.knowledge_links)

        with st.expander("🧩 相似题推荐", expanded=False):
            render_similar_items_panel(domain="deeplearning", item_id=item.item_id)

    with right:
        if item.problem_type == "choice":
            _render_choice(item)
        elif item.problem_type == "fill":
            _render_fill(item)
        elif item.problem_type == "code":
            _render_code(item)

        g = st.session_state.agent_grades.get(problem_key("deeplearning", item.item_id))
        if g:
            render_ai_teacher_grade(title="AI老师批改", text=g)
    
    # AI 教师对话
    render_ai_teacher_chat(
        context_type="problem",
        context_id=item.item_id,
        context_data={
            "domain": "深度学习",
            "title": item.title,
            "prompt": item.prompt,
            "difficulty": item.difficulty,
            "explanation": getattr(item, "explanation", ""),
        },
        key_prefix="dl_",
    )


def _render_choice(item) -> None:
    st.markdown("### ✏️ 选择答案")

    if st.session_state.dl_result:
        for opt in item.options:
            opt_key = opt[0]
            if opt_key == item.correct_option:
                st.success(f"✅ {opt}")
            elif opt_key == st.session_state.dl_selected_option:
                st.error(f"❌ {opt}")
            else:
                st.write(opt)

        if st.session_state.dl_result.get("correct"):
            st.success("🎉 正确！")
        else:
            st.error(f"正确答案是 {item.correct_option}")

        with st.expander("📖 解析"):
            st.markdown(item.explanation)

        if st.button("AI老师批改", width="stretch", disabled=(not AI_ENABLED)):
            with st.spinner("Agent 批改中..."):
                text = agent_grade_dl(
                    problem=item,
                    user_state={"selected": st.session_state.dl_selected_option, "result": st.session_state.dl_result},
                )
                st.session_state.agent_grades[problem_key("deeplearning", item.item_id)] = text
            record_attempt(ptype="deeplearning", pid=item.item_id, event="agent_grade", ok=None)
            st.rerun()
    else:
        for opt in item.options:
            opt_key = opt[0]
            if st.button(opt, key=f"opt_{item.item_id}_{opt_key}", width="stretch"):
                st.session_state.dl_selected_option = opt_key

        if st.session_state.dl_selected_option:
            if st.button("✅ 提交", type="primary", width="stretch"):
                ok = st.session_state.dl_selected_option == item.correct_option
                st.session_state.dl_result = {"correct": ok}
                record_attempt(
                    ptype="deeplearning",
                    pid=item.item_id,
                    event="submit_choice",
                    ok=ok,
                    meta={"picked": st.session_state.dl_selected_option, "answer": item.correct_option},
                )
                mark_completed(ptype="deeplearning", pid=item.item_id)
                mark_checked(ptype="deeplearning", pid=item.item_id, correct=ok)
                st.rerun()


def _render_fill(item) -> None:
    st.markdown("### ✏️ 填空")

    fill = st.session_state.dl_fill_answers
    for bid in item.blanks.keys():
        fill[bid] = st.text_input(f"填空 {bid}：", value=fill.get(bid, ""), key=f"fill_{item.item_id}_{bid}")
    st.session_state.dl_fill_answers = fill

    if not st.session_state.dl_result:
        if st.button("✅ 提交", type="primary", width="stretch"):
            cnt = sum(
                1 for b, a in item.blanks.items() if fill.get(b, "").strip().lower() in [x.lower() for x in a]
            )
            ok = cnt == len(item.blanks)
            st.session_state.dl_result = {"correct": ok, "count": cnt}
            record_attempt(
                ptype="deeplearning",
                pid=item.item_id,
                event="submit_fill",
                ok=ok,
                meta={"count": cnt, "total": len(item.blanks)},
            )
            mark_completed(ptype="deeplearning", pid=item.item_id)
            mark_checked(ptype="deeplearning", pid=item.item_id, correct=ok)
            st.rerun()

    if st.session_state.dl_result:
        if st.session_state.dl_result.get("correct"):
            st.success("🎉 正确！")
        else:
            st.warning(f"正确 {st.session_state.dl_result.get('count', 0)}/{len(item.blanks)}")

        with st.expander("📖 解析"):
            st.markdown(item.explanation)

        if st.button("AI老师批改", width="stretch", disabled=(not AI_ENABLED)):
            with st.spinner("Agent 批改中..."):
                text = agent_grade_dl(problem=item, user_state={"fills": fill, "result": st.session_state.dl_result})
                st.session_state.agent_grades[problem_key("deeplearning", item.item_id)] = text
            record_attempt(ptype="deeplearning", pid=item.item_id, event="agent_grade", ok=None)
            st.rerun()


def _render_code(item) -> None:
    st.markdown("### ✏️ 代码")

    code = st_ace(
        value=st.session_state.dl_code or item.starter_code,
        language="python",
        theme="github",
        key=f"dl_ace_{item.item_id}",
        height=280,
        auto_update=True,
    )
    st.session_state.dl_code = code if isinstance(code, str) else st.session_state.dl_code

    tests = (item.grader or {}).get("tests", [])

    b1, b2 = st.columns(2)

    with b1:
        if st.button("▶️ 运行", type="primary", width="stretch"):
            r = run_tests(
                user_code=st.session_state.dl_code,
                func_name=item.function_name,
                tests=tests,
                timeout_s=2.0,
            ).to_json()
            st.session_state.dl_result = r
            record_attempt(
                ptype="deeplearning",
                pid=item.item_id,
                event="run_tests",
                ok=bool(r.get("ok")),
                meta={"passed": r.get("passed"), "total": r.get("total")},
            )
            if r.get("ok"):
                mark_completed(ptype="deeplearning", pid=item.item_id)
                mark_checked(ptype="deeplearning", pid=item.item_id, correct=True)
            st.rerun()

    with b2:
        if st.button("🔄 重置", width="stretch"):
            st.session_state.dl_code = item.starter_code
            st.session_state.dl_result = None
            st.rerun()

    if st.session_state.dl_result:
        r = st.session_state.dl_result
        if r.get("ok"):
            st.success(f"🎉 通过！{r.get('passed')}/{r.get('total')}")
        else:
            st.error(f"❌ {r.get('passed', 0)}/{r.get('total', 0)}")

        if st.button("AI老师批改", width="stretch", disabled=(not AI_ENABLED)):
            with st.spinner("Agent 批改中..."):
                text = agent_grade_dl(problem=item, user_state={"code": st.session_state.dl_code, "test_result": r})
                st.session_state.agent_grades[problem_key("deeplearning", item.item_id)] = text
            record_attempt(ptype="deeplearning", pid=item.item_id, event="agent_grade", ok=None)
            st.rerun()
