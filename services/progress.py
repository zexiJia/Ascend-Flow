# filename: services/progress.py
"""进度追踪服务 - 管理每日学习进度"""
from __future__ import annotations

from datetime import date
from typing import Any, Dict

import streamlit as st

from services.user_store import maybe_persist_progress

def today_key() -> str:
    """返回今日日期字符串作为 key"""
    return date.today().isoformat()


def get_today_progress() -> Dict[str, Any]:
    """
    获取今日进度数据。
    
    结构:
    {
      "completed": { "coding:0001": True, ... },   # 完成状态
      "correct": { "coding:0001": True, ... },     # 仅客观/自评后才写入
      "checked": { "coding:0001": True, ... },     # 用于计算正确率分母
      "attempts": [ {..}, ... ]                     # 尝试记录
    }
    """
    today = today_key()
    pb = st.session_state.progress_by_date
    pb.setdefault(today, {"completed": {}, "correct": {}, "checked": {}, "attempts": []})
    return pb[today]


def problem_key(ptype: str, pid: str) -> str:
    """生成题目唯一 key"""
    return f"{ptype}:{pid}"


def record_attempt(
    *,
    ptype: str,
    pid: str,
    event: str,
    ok: bool | None = None,
    meta: Dict[str, Any] | None = None,
) -> None:
    """记录一次答题尝试"""
    prog = get_today_progress()
    prog["attempts"].append(
        {
            "t": today_key(),
            "key": problem_key(ptype, pid),
            "ptype": ptype,
            "pid": pid,
            "event": event,
            "ok": ok,
            "meta": meta or {},
        }
    )
    maybe_persist_progress()


def mark_completed(*, ptype: str, pid: str) -> None:
    """标记题目为已完成"""
    prog = get_today_progress()
    prog["completed"][problem_key(ptype, pid)] = True
    maybe_persist_progress()


def mark_checked(*, ptype: str, pid: str, correct: bool) -> None:
    """标记题目已判题及正确性"""
    prog = get_today_progress()
    k = problem_key(ptype, pid)
    prog["checked"][k] = True
    prog["correct"][k] = bool(correct)
    maybe_persist_progress()


def get_all_progress_dates() -> list[str]:
    """获取所有有记录的日期列表（倒序）"""
    pb = st.session_state.progress_by_date
    dates = sorted(pb.keys(), reverse=True)
    return dates


def get_progress_by_date(date_key: str) -> Dict[str, Any]:
    """获取指定日期的进度数据"""
    pb = st.session_state.progress_by_date
    return pb.get(date_key, {"completed": {}, "correct": {}, "checked": {}, "attempts": []})


def get_date_summary(date_key: str) -> Dict[str, Any]:
    """获取指定日期的学习摘要"""
    prog = get_progress_by_date(date_key)
    completed_count = len(prog["completed"])
    checked_count = len(prog["checked"])
    correct_count = sum(1 for v in prog["correct"].values() if v)
    acc = (correct_count / checked_count) if checked_count else 0.0
    
    return {
        "date": date_key,
        "completed": completed_count,
        "checked": checked_count,
        "correct": correct_count,
        "accuracy": acc,
        "attempts": len(prog["attempts"]),
    }

