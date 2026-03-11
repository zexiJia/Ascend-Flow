"""Lightweight local Python code evaluator"""
from __future__ import annotations

import json
import multiprocessing as mp
import io
import contextlib
import textwrap
import traceback
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


def _safe_jsonable(x: Any) -> Any:
    """尽量把对象转成可 JSON 序列化的形式，避免 to_json 崩溃。"""
    try:
        json.dumps(x, ensure_ascii=False)
        return x
    except Exception:
        try:
            return repr(x)
        except Exception:
            return "<unserializable>"


@dataclass(frozen=True)
class TestFailure:
    name: str
    args: Any
    expected: Any
    got: Any
    error: Optional[str] = None
    traceback: Optional[str] = None


@dataclass(frozen=True)
class TestCaseResult:
    name: str
    args: Any
    expected: Any
    got: Any
    passed: bool
    stdout: str = ""
    error: Optional[str] = None
    traceback: Optional[str] = None


@dataclass(frozen=True)
class TestRunResult:
    ok: bool
    passed: int
    total: int
    failures: List[TestFailure]
    runtime_error: Optional[str] = None
    cases: List[TestCaseResult] = None

    def to_json(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "passed": self.passed,
            "total": self.total,
            "cases": [
                {
                    "name": c.name,
                    "args": _safe_jsonable(c.args),
                    "expected": _safe_jsonable(c.expected),
                    "got": _safe_jsonable(c.got),
                    "passed": bool(c.passed),
                    "stdout": c.stdout,
                    "error": c.error,
                    "traceback": c.traceback,
                }
                for c in (self.cases or [])
            ],
            "failures": [
                {
                    "name": f.name,
                    "args": _safe_jsonable(f.args),
                    "expected": _safe_jsonable(f.expected),
                    "got": _safe_jsonable(f.got),
                    "error": f.error,
                    "traceback": f.traceback,
                }
                for f in self.failures
            ],
            "runtime_error": self.runtime_error,
        }


def _worker_exec_and_run(
    user_code: str,
    func_name: str,
    tests: List[Dict[str, Any]],
    q: mp.Queue,
) -> None:
    try:
        glb: Dict[str, Any] = {}
        loc: Dict[str, Any] = {}
        compiled = compile(user_code, "<user_code>", "exec")
        exec(compiled, glb, loc)
        fn = loc.get(func_name) or glb.get(func_name)
        if fn is None or not callable(fn):
            q.put({"_error": f"找不到函数 `{func_name}`。请确认函数名和签名没有改。"})
            return

        failures: List[Dict[str, Any]] = []
        cases: List[Dict[str, Any]] = []
        passed = 0
        for t in tests:
            name = t.get("name", "case")
            args = t.get("args", [])
            expected = t.get("expected")
            try:
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                    if isinstance(args, list):
                        got = fn(*args)
                    else:
                        got = fn(args)
                out = buf.getvalue()
                ok = got == expected
                if ok:
                    passed += 1
                else:
                    failures.append(
                        {"name": name, "args": args, "expected": expected, "got": got, "error": None, "traceback": None}
                    )
                cases.append(
                    {
                        "name": name,
                        "args": args,
                        "expected": expected,
                        "got": got,
                        "passed": ok,
                        "stdout": out,
                        "error": None,
                        "traceback": None,
                    }
                )
            except Exception as e:
                tb = traceback.format_exc()
                cases.append(
                    {
                        "name": name,
                        "args": args,
                        "expected": expected,
                        "got": None,
                        "passed": False,
                        "stdout": "",
                        "error": f"{type(e).__name__}: {e}",
                        "traceback": tb,
                    }
                )
                failures.append(
                    {
                        "name": name,
                        "args": args,
                        "expected": expected,
                        "got": None,
                        "error": f"{type(e).__name__}: {e}",
                        "traceback": tb,
                    }
                )

        q.put({"passed": passed, "total": len(tests), "failures": failures, "cases": cases})
    except Exception as e:
        q.put({"_error": f"{type(e).__name__}: {e}", "_traceback": traceback.format_exc()})


def run_tests(
    *,
    user_code: str,
    func_name: str,
    tests: List[Dict[str, Any]],
    timeout_s: float = 1.5,
) -> TestRunResult:
    """
    Lightweight local evaluator:
    - runs code in a subprocess
    - per whole run timeout (not per case) to keep it simple
    """
    user_code = textwrap.dedent(user_code).strip() + "\n"

    # macOS 默认 spawn，在某些执行环境里会遇到 <stdin> 等不可导入路径问题；
    # 优先使用 fork（若可用）提高兼容性。
    try:
        ctx = mp.get_context("fork")
    except Exception:
        ctx = mp.get_context()

    q: mp.Queue = ctx.Queue()
    p = ctx.Process(target=_worker_exec_and_run, args=(user_code, func_name, tests, q))
    p.start()
    p.join(timeout=timeout_s)
    if p.is_alive():
        p.terminate()
        p.join(timeout=0.2)
        return TestRunResult(
            ok=False,
            passed=0,
            total=len(tests),
            failures=[],
            runtime_error=f"超时：运行超过 {timeout_s:.1f}s（可能是死循环或复杂度太高）",
            cases=[],
        )

    if q.empty():
        return TestRunResult(ok=False, passed=0, total=len(tests), failures=[], runtime_error="运行失败：无返回结果", cases=[])

    payload = q.get()
    if "_error" in payload:
        tb = payload.get("_traceback")
        msg = payload["_error"]
        if tb:
            msg = msg + "\n\n" + tb
        return TestRunResult(ok=False, passed=0, total=len(tests), failures=[], runtime_error=msg, cases=[])

    failures = [
        TestFailure(
            name=f.get("name", "case"),
            args=f.get("args"),
            expected=f.get("expected"),
            got=f.get("got"),
            error=f.get("error"),
            traceback=f.get("traceback"),
        )
        for f in payload.get("failures", [])
    ]
    cases = [
        TestCaseResult(
            name=c.get("name", "case"),
            args=c.get("args"),
            expected=c.get("expected"),
            got=c.get("got"),
            passed=bool(c.get("passed", False)),
            stdout=(c.get("stdout") or ""),
            error=c.get("error"),
            traceback=c.get("traceback"),
        )
        for c in payload.get("cases", [])
    ]
    passed = int(payload.get("passed", 0))
    total = int(payload.get("total", len(tests)))
    ok = passed == total and len(failures) == 0
    return TestRunResult(ok=ok, passed=passed, total=total, failures=failures, runtime_error=None, cases=cases)

