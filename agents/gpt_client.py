"""ichat gateway client for GPT-4o calls"""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import time
from typing import Any, Dict, List, Optional, Tuple

import requests

DEFAULT_MODEL = "gpt-4o"
DEFAULT_ENDPOINT = "http://ichat.woa.com/api/chat_completions"


def _calc_authorization(source: str, appkey: str) -> Tuple[str, str]:
    """HMAC signature depends on timestamp, so compute inside call."""
    timestamp = str(int(time.time()))
    sign_str = "x-timestamp: %s\nx-source: %s" % (timestamp, source)
    sign = hmac.new(appkey.encode("utf-8"), sign_str.encode("utf-8"), hashlib.sha256).digest()
    return sign.hex(), timestamp


def _env(name: str) -> str:
    v = (os.getenv(name) or "").strip()
    if not v:
        raise RuntimeError(f"Missing env var: {name}")
    return v


def ichat_chat_completions(
    *,
    messages: List[Dict[str, Any]],
    model: str = DEFAULT_MODEL,
    max_tokens: int = 800,
    temperature: float = 0.4,
    endpoint: str = DEFAULT_ENDPOINT,
    appid: Optional[str] = None,
    appkey: Optional[str] = None,
    source: Optional[str] = None,
    timeout_s: float = 60.0,
) -> Tuple[str, Dict[str, Any]]:
    """
    Calls ichat gateway using HMAC header scheme.
    Returns: (assistant_text, raw_json)
    """
    appid = (appid or os.getenv("ICHAT_APPID") or "").strip() or _env("ICHAT_APPID")
    appkey = (appkey or os.getenv("ICHAT_APPKEY") or "").strip() or _env("ICHAT_APPKEY")
    source = (source or os.getenv("ICHAT_SOURCE") or "").strip() or _env("ICHAT_SOURCE")

    auth, timestamp = _calc_authorization(source, appkey)
    headers = {
        "X-AppID": appid,
        "X-Source": source,
        "X-Timestamp": timestamp,
        "X-Authorization": auth,
    }

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": int(max_tokens),
        "temperature": float(temperature),
    }

    resp = requests.post(endpoint, headers=headers, json=payload, timeout=timeout_s)
    obj = resp.json()

    text = ""
    try:
        choices = obj.get("choices") or []
        if choices:
            msg = (choices[0] or {}).get("message") or {}
            text = (msg.get("content") or "").strip()
    except Exception:
        text = ""
    if not text:
        text = str(obj.get("response") or "").strip()

    return text, obj


def image_bytes_to_data_url(image_bytes: bytes, *, mime: str) -> str:
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def make_vision_message(*, prompt: str, image_data_url: str) -> List[Dict[str, Any]]:
    return [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_data_url}},
            ],
        }
    ]

