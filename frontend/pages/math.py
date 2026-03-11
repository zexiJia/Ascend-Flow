# filename: frontend/pages/math.py
"""数学题页面渲染"""

from __future__ import annotations

import streamlit as st

from problems.math.loader import get_math_item_by_id
from services.progress import problem_key, record_attempt, mark_completed, mark_checked
from services.ai_grader import AI_ENABLED, agent_grade_math
from frontend.pages.common import render_ai_teacher_grade
from frontend.pages._item_panels import render_item_knowledge_panel, render_similar_items_panel
from frontend.components.ai_chat import render_ai_teacher_chat


# 题型中文名
PROBLEM_TYPE_NAMES = {
    "single_choice": "单选题",
    "multi_choice": "多选题",
    "fill": "填空题",
    "solve": "解答题",
}


def render_math_problem() -> None:
    """渲染数学题页面"""
    item = get_math_item_by_id(st.session_state.current_problem_id)
    if not item:
        st.error("题目不存在")
        return

    cat_labels = {
        "calculus": "微积分",
        "probability": "概率论",
        "linear_algebra": "线性代数",
    }
    cat_label = cat_labels.get(item.category, item.category)
    ptype_name = PROBLEM_TYPE_NAMES.get(item.problem_type, item.problem_type)

    st.markdown(f"## 📐 {item.title}")
    st.caption(f"分类：{cat_label} | 题型：{ptype_name} | 难度：{item.difficulty}/10")

    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown("### 📋 题目")
        st.latex(item.prompt)

        with st.expander("🧠 知识点", expanded=True):
            render_item_knowledge_panel(domain="math", item_id=item.item_id, knowledge_links=item.knowledge_links)

        with st.expander("🧩 相似题推荐", expanded=False):
            render_similar_items_panel(domain="math", item_id=item.item_id)

    with right:
        if item.problem_type == "single_choice":
            _render_single_choice(item)
        elif item.problem_type == "multi_choice":
            _render_multi_choice(item)
        elif item.problem_type == "fill":
            _render_fill(item)
        else:
            _render_solve(item)

        g = st.session_state.agent_grades.get(problem_key("math", item.item_id))
        if g:
            render_ai_teacher_grade(title="AI老师批改", text=g)
    
    # AI 教师对话
    render_ai_teacher_chat(
        context_type="problem",
        context_id=item.item_id,
        context_data={
            "domain": "数学",
            "title": item.title,
            "prompt": item.prompt,
            "difficulty": item.difficulty,
            "explanation": getattr(item, "explanation", ""),
        },
        key_prefix="math_",
    )


def _render_single_choice(item) -> None:
    st.markdown("### ✏️ 单选")

    if st.session_state.math_result:
        for opt in item.options:
            opt_key = opt[0]
            if opt_key == item.correct_option:
                st.success(f"✅ {opt}")
            elif opt_key == st.session_state.math_selected_option:
                st.error(f"❌ {opt}")
            else:
                st.write(opt)

        if st.session_state.math_result.get("correct"):
            st.success("🎉 正确！")
        else:
            st.error(f"正确答案是 {item.correct_option}")

        if item.explanation:
            with st.expander("📖 解析"):
                st.markdown(item.explanation)

        if st.button("AI老师批改", width="stretch", disabled=(not AI_ENABLED)):
            with st.spinner("Agent 批改中..."):
                text = agent_grade_math(problem=item, answer=f"选择了{st.session_state.math_selected_option}")
                st.session_state.agent_grades[problem_key("math", item.item_id)] = text
            st.rerun()
    else:
        for opt in item.options:
            opt_key = opt[0]
            if st.button(opt, key=f"math_opt_{item.item_id}_{opt_key}", width="stretch"):
                st.session_state.math_selected_option = opt_key

        if st.session_state.math_selected_option:
            if st.button("✅ 提交", type="primary", width="stretch"):
                ok = st.session_state.math_selected_option == item.correct_option
                st.session_state.math_result = {"correct": ok}
                record_attempt(ptype="math", pid=item.item_id, event="submit_choice", ok=ok)
                mark_completed(ptype="math", pid=item.item_id)
                mark_checked(ptype="math", pid=item.item_id, correct=ok)
                st.rerun()


def _render_multi_choice(item) -> None:
    st.markdown("### ✏️ 多选")

    if st.session_state.math_result:
        correct_set = set(item.correct_option)
        selected_set = set(st.session_state.math_selected_options)

        for opt in item.options:
            opt_key = opt[0]
            if opt_key in correct_set:
                st.success(f"✅ {opt}")
            elif opt_key in selected_set:
                st.error(f"❌ {opt}")
            else:
                st.write(opt)

        if st.session_state.math_result.get("correct"):
            st.success("🎉 正确！")
        else:
            st.error(f"正确答案是 {item.correct_option}")

        if item.explanation:
            with st.expander("📖 解析"):
                st.markdown(item.explanation)

        if st.button("AI老师批改", width="stretch", disabled=(not AI_ENABLED)):
            with st.spinner("Agent 批改中..."):
                text = agent_grade_math(problem=item, answer=f"选择了{''.join(st.session_state.math_selected_options)}")
                st.session_state.agent_grades[problem_key("math", item.item_id)] = text
            st.rerun()
    else:
        selected = st.session_state.math_selected_options
        for opt in item.options:
            opt_key = opt[0]
            checked = st.checkbox(opt, value=(opt_key in selected), key=f"math_multi_{item.item_id}_{opt_key}")
            if checked and opt_key not in selected:
                selected.append(opt_key)
            elif not checked and opt_key in selected:
                selected.remove(opt_key)
        st.session_state.math_selected_options = selected

        if selected:
            if st.button("✅ 提交", type="primary", width="stretch"):
                ok = set(selected) == set(item.correct_option)
                st.session_state.math_result = {"correct": ok}
                record_attempt(ptype="math", pid=item.item_id, event="submit_multi", ok=ok)
                mark_completed(ptype="math", pid=item.item_id)
                mark_checked(ptype="math", pid=item.item_id, correct=ok)
                st.rerun()


def _render_fill(item) -> None:
    st.markdown("### ✏️ 填空")

    fill = st.session_state.math_fill_answers
    for bid in item.blanks.keys():
        fill[bid] = st.text_input(f"第 {bid} 空：", value=fill.get(bid, ""), key=f"math_fill_{item.item_id}_{bid}")
    st.session_state.math_fill_answers = fill

    if not st.session_state.math_result:
        if st.button("✅ 提交", type="primary", width="stretch"):
            cnt = sum(
                1 for b, a in item.blanks.items() if fill.get(b, "").strip().lower() in [x.lower() for x in a]
            )
            ok = cnt == len(item.blanks)
            st.session_state.math_result = {"correct": ok, "count": cnt}
            record_attempt(ptype="math", pid=item.item_id, event="submit_fill", ok=ok)
            mark_completed(ptype="math", pid=item.item_id)
            mark_checked(ptype="math", pid=item.item_id, correct=ok)
            st.rerun()

    if st.session_state.math_result:
        if st.session_state.math_result.get("correct"):
            st.success("🎉 正确！")
        else:
            st.warning(f"正确 {st.session_state.math_result.get('count', 0)}/{len(item.blanks)}")

        if item.explanation:
            with st.expander("📖 解析"):
                st.markdown(item.explanation)

        if st.button("AI老师批改", width="stretch", disabled=(not AI_ENABLED)):
            with st.spinner("Agent 批改中..."):
                text = agent_grade_math(problem=item, answer=str(fill))
                st.session_state.agent_grades[problem_key("math", item.item_id)] = text
            st.rerun()


def _render_solve(item) -> None:
    st.markdown("### ✏️ 解答")

    answer = st.text_area("写下你的解题过程：", value=st.session_state.user_math_answer, height=250)
    st.session_state.user_math_answer = answer

    b1, b2 = st.columns(2)

    with b1:
        if st.button("✅ 提交", type="primary", width="stretch"):
            st.session_state.math_result = {"submitted": True}
            record_attempt(ptype="math", pid=item.item_id, event="submit", ok=None, meta={"len": len(answer.strip())})
            mark_completed(ptype="math", pid=item.item_id)
            st.rerun()

    with b2:
        if st.button("👁️ 查看答案", width="stretch"):
            st.session_state.math_result = {"show_answer": True}
            st.rerun()

    if st.session_state.math_result:
        if st.session_state.math_result.get("show_answer") or st.session_state.math_result.get("submitted"):
            st.success("**参考答案：**")
            st.latex(item.expected_answer_latex)

            if item.explanation:
                with st.expander("📖 解析"):
                    st.markdown(item.explanation)

            self_eval = st.radio(
                "自评：",
                ["不确定", "我做对了", "我做错了"],
                horizontal=True,
                key=f"math_self_{item.item_id}",
            )

            c1, c2 = st.columns(2)
            with c1:
                if st.button("保存自评", width="stretch"):
                    if self_eval == "我做对了":
                        mark_checked(ptype="math", pid=item.item_id, correct=True)
                    elif self_eval == "我做错了":
                        mark_checked(ptype="math", pid=item.item_id, correct=False)
                    record_attempt(ptype="math", pid=item.item_id, event="self_eval", ok=None, meta={"self": self_eval})
                    st.success("已记录")

            with c2:
                if st.button("AI老师批改", width="stretch", disabled=(not AI_ENABLED)):
                    with st.spinner("Agent 批改中..."):
                        text = agent_grade_math(problem=item, answer=answer)
                        st.session_state.agent_grades[problem_key("math", item.item_id)] = text
                    st.rerun()
