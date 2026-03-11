"""AI 批改服务 - 封装 AI Agent 调用"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

from problems.coding.loader import CodingItem
from problems.math.loader import MathItem
from problems.deeplearning.loader import DLItem

AI_ENABLED = bool(os.getenv("ICHAT_APPID") and os.getenv("ICHAT_APPKEY") and os.getenv("ICHAT_SOURCE"))


def agent_call(prompt: str, *, max_tokens: int = 900, temperature: float = 0.4) -> str:
    if not AI_ENABLED:
        return "⚠️ 未配置 AI（ICHAT_APPID/ICHAT_APPKEY/ICHAT_SOURCE）。"

    from agents.gpt_client import ichat_chat_completions

    text, _ = ichat_chat_completions(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return (text or "").strip() or "（AI 未返回内容）"


def ai_today_summary(prompt: str) -> str:
    return agent_call(prompt, max_tokens=700, temperature=0.4)


def ai_lesson_tutor(prompt: str) -> str:
    return agent_call(prompt, max_tokens=1200, temperature=0.45)


def agent_grade_coding(*, problem: CodingItem, user_code: str, test_result: Optional[Dict[str, Any]]) -> str:
    tr = test_result or {}
    
    # 根据是否有测试结果，构建不同的提示
    if tr and tr.get("total"):
        test_info = f"本地测试结果：passed={tr.get('passed')} total={tr.get('total')} ok={tr.get('ok')}\n错误信息：{tr.get('runtime_error')}\n"
    else:
        test_info = "（未运行测试，请根据代码逻辑分析是否正确）\n"
    
    prompt = (
        "你是代码教练 Agent。请对学生解答做「批改 + 建议」。\n\n"
        "【重要】输出要求：\n"
        "- 必须全部使用中文输出\n"
        "- 使用清晰的结构化格式\n\n"
        "输出结构：\n"
        "## 批改结论\n"
        "（代码是否正确/主要问题）\n\n"
        "## 代码分析\n"
        "（分析代码逻辑是否正确）\n\n"
        "## 改进建议\n"
        "1. （第一条建议）\n"
        "2. （第二条建议）\n\n"
        "## 重点提示\n"
        "（若有问题：指出最可能的 bug 点 + 最小修改方向，不要直接给完整答案）\n"
        "（若正确：给 1 条性能/可读性提升建议）\n\n"
        "---\n"
        f"题目：{problem.title}\n"
        f"难度：{problem.difficulty}/10\n"
        f"题干：\n{problem.prompt}\n\n"
        f"函数签名：{problem.function_signature}\n"
        f"学生代码：\n```python\n{user_code}\n```\n"
        f"{test_info}"
    )
    return agent_call(prompt, max_tokens=1000, temperature=0.35)


def agent_grade_math(*, problem: MathItem, answer: str) -> str:
    rubric = [
        {"id": s.step_id, "desc": s.desc, "points": s.points, "tags": s.common_mistake_tags}
        for s in (problem.rubric or [])
    ]
    prompt = (
        "你是数学批改 Agent。请根据 rubric 对学生解答进行过程性评分。\n\n"
        "【极其重要】输出格式要求：\n"
        "1. 必须严格输出合法的 JSON 格式，不要输出任何 markdown 代码块标记（不要```json）\n"
        "2. 所有字符串内容必须使用中文\n"
        "3. JSON 必须可以被 Python json.loads() 正确解析\n"
        "4. 不要在 JSON 前后添加任何额外文字\n\n"
        "严格按照以下 JSON 结构输出（直接输出JSON，不要任何包裹）：\n"
        '{"score": 得分数字, "total": 满分数字, "per_step": [{"step_id": "步骤ID", "points": 得分数字, "comment": "中文评语", "mistake_tags": ["错误标签"]}], "overall_comment": "中文总体评价", "next_practice": ["中文练习建议1", "中文练习建议2"]}\n\n'
        "---\n"
        f"题目：{problem.title}\n"
        f"题干(LaTeX)：{problem.prompt}\n"
        f"参考答案(LaTeX)：{problem.expected_answer_latex}\n"
        f"rubric：{rubric}\n"
        f"学生解答：\n{answer}\n"
    )
    return agent_call(prompt, max_tokens=900, temperature=0.3)


def agent_grade_dl(*, problem: DLItem, user_state: Dict[str, Any]) -> str:
    prompt = (
        "你是深度学习学习教练 Agent。请对学生作答进行批改与提升建议。\n\n"
        "【重要】输出要求：\n"
        "- 必须全部使用中文输出\n"
        "- 使用清晰的结构化格式\n"
        "- 不要长篇大论，总长度<=250字\n\n"
        "输出结构：\n"
        "## 判定结果\n"
        "（对/错/部分正确）\n\n"
        "## 概念回顾\n"
        "（核心概念简述）\n\n"
        "## 误区分析\n"
        "（如有错误，指出误区）\n\n"
        "## 纠正建议\n"
        "（如何正确理解）\n\n"
        "## 小练习\n"
        "（1个巩固小问题）\n\n"
        "---\n"
        f"题目：{problem.title}\n"
        f"类型：{problem.problem_type}\n"
        f"题干：{problem.prompt}\n"
        f"选项：{problem.options}\n"
        f"标准答案：{problem.correct_option}\n"
        f"填空标准：{problem.blanks}\n"
        f"解释：{problem.explanation}\n"
        f"学生作答状态：{user_state}\n"
    )
    return agent_call(prompt, max_tokens=700, temperature=0.35)
