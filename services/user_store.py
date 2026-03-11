"""用户数据持久化（本地 JSON）"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

import streamlit as st


_DATA_DIR = Path(__file__).resolve().parents[1] / "user_data"


def authenticate(username: str, password: str) -> bool:
    """验证登录（当前仅提供测试账号）"""
    return username == "test" and password == "123123"


def _user_file(username: str) -> Path:
    safe = "".join(ch for ch in username if ch.isalnum() or ch in ("-", "_")).strip() or "user"
    return _DATA_DIR / f"{safe}.json"


def load_user_progress(username: str) -> Dict[str, Any]:
    """读取用户进度（progress_by_date）"""
    path = _user_file(username)
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        pb = raw.get("progress_by_date", {})
        return pb if isinstance(pb, dict) else {}
    except Exception:
        return {}


def save_user_progress(username: str, progress_by_date: Dict[str, Any]) -> None:
    """保存用户进度（progress_by_date）"""
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = _user_file(username)
    payload = {"progress_by_date": progress_by_date}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def maybe_persist_progress() -> None:
    """若已登录则持久化当前 session 的 progress_by_date"""
    if not st.session_state.get("logged_in"):
        return
    username = st.session_state.get("current_user")
    if not username:
        return
    pb = st.session_state.get("progress_by_date", {})
    if isinstance(pb, dict):
        save_user_progress(username, pb)


