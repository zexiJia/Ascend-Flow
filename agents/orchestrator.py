"""Orchestration functions for multi-agent group chat stages"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List

from agents.bundle import AgentBundle, apply_allowed_transitions, reset_groupchat


@dataclass(frozen=True)
class OrchestratorResult:
    final_json: Dict[str, Any]
    transcript: List[Dict[str, str]]


def _extract_json(text: str) -> Dict[str, Any]:
    text = (text or "").strip()
    if not text:
        return {"_error": "empty"}
    try:
        return json.loads(text)
    except Exception:
        pass
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        return {"_error": "json_parse_failed", "_raw": text[:8000]}
    try:
        return json.loads(m.group(0))
    except Exception:
        return {"_error": "json_parse_failed", "_raw": text[:8000]}


def _collect_transcript(bundle: AgentBundle) -> List[Dict[str, str]]:
    msgs = bundle.manager.groupchat.messages
    out: List[Dict[str, str]] = []
    for m in msgs:
        name = str(m.get("name") or m.get("role") or "Unknown")
        content = m.get("content")
        if isinstance(content, list):
            parts = []
            for p in content:
                if isinstance(p, dict) and p.get("type") == "text":
                    parts.append(str(p.get("text", "")))
            content_s = "\n".join([x for x in parts if x]).strip()
        else:
            content_s = str(content or "").strip()
        if not content_s:
            continue
        out.append({"speaker": name, "content": content_s})
    return out


def run_group_stage(bundle: AgentBundle, *, stage: str, prompt: str) -> OrchestratorResult:
    reset_groupchat(bundle)
    apply_allowed_transitions(bundle, stage=stage)
    stage_prompt = prompt.strip() + "\n\nNow coordinate the team quickly, then output FINAL_JSON only."
    bundle.user.initiate_chat(bundle.manager, message=stage_prompt)
    transcript = _collect_transcript(bundle)
    last = transcript[-1]["content"] if transcript else ""
    final_json = _extract_json(last)
    return OrchestratorResult(final_json=final_json, transcript=transcript)


def daily_drop(
    bundle: AgentBundle,
    *,
    coding_pool: List[Dict[str, Any]],
    calculus_pool: List[Dict[str, Any]],
    date_yyyy_mm_dd: str,
) -> OrchestratorResult:
    prompt = f"""
You are running Daily Drop for Ascend Flow on date={date_yyyy_mm_dd}.

Task:
- Pick exactly 1 Coding problem and 1 Calculus problem from the provided pools.
- Planner should lead the selection; Motivator adds one pacing suggestion.

Constraints:
- Use only the given problem_ids.
- Keep copy short, coachy, spoken Chinese.
- Difficulty tag: one of ["Easy","Warmup","Steady","Spicy"].

Return FINAL_JSON with schema:
{{
  "daily_drop": [
    {{"track":"coding","problem_id":"0001","goal":"...","est_minutes":25,"reason":"...","difficulty_tag":"..."}},
    {{"track":"calculus","problem_id":"C1","goal":"...","est_minutes":25,"reason":"...","difficulty_tag":"..."}}
  ],
  "pacing": {{"tone":"...","message":"..."}}
}}

Coding pool:
{json.dumps(coding_pool, ensure_ascii=False)}

Calculus pool:
{json.dumps(calculus_pool, ensure_ascii=False)}
""".strip()
    return run_group_stage(bundle, stage="daily_drop", prompt=prompt)


def concept_check_generate(bundle: AgentBundle, *, track: str, problem: Dict[str, Any]) -> OrchestratorResult:
    prompt = f"""
Concept Check (generate) for track={track}.

Problem:
{json.dumps(problem, ensure_ascii=False)}

Tutor leads. Reviewer may add "expected_points" additions.

Return FINAL_JSON schema:
{{
  "explain":"<=120 Chinese chars",
  "check_question":"one question",
  "expected_points":["...","..."]
}}
""".strip()
    return run_group_stage(bundle, stage="concept", prompt=prompt)


def concept_check_grade(
    bundle: AgentBundle,
    *,
    track: str,
    problem: Dict[str, Any],
    explain_pack: Dict[str, Any],
    user_answer: str,
) -> OrchestratorResult:
    prompt = f"""
Concept Check (grade) for track={track}.

Problem:
{json.dumps(problem, ensure_ascii=False)}

Tutor's previous pack:
{json.dumps(explain_pack, ensure_ascii=False)}

User answer:
{user_answer}

Return FINAL_JSON schema:
{{
  "feedback":"短评：对/不对/差在哪",
  "alt_explain":{{"style":"analogy|rigorous|engineering","text":"..."}},
  "next_check_question":"one follow-up question"
}}
""".strip()
    return run_group_stage(bundle, stage="concept", prompt=prompt)


def l1_generate(bundle: AgentBundle, *, track: str, problem: Dict[str, Any]) -> OrchestratorResult:
    prompt = f"""
Generate L1 scaffold for track={track}.
Examiner leads.

Problem:
{json.dumps(problem, ensure_ascii=False)}

Return FINAL_JSON schema:
{{
  "l1_prompt":"markdown text; for coding include code skeleton with blanks; for calculus ask to fill one key step",
  "l1_answer_key":{{"blanks":{{"BLANK1":"...","BLANK2":"..."}}, "notes":"short"}},
  "l3_variant_prompt":"text only",
  "variant_skill_tag":"one short tag"
}}
""".strip()
    return run_group_stage(bundle, stage="l1", prompt=prompt)


def l3_generate(bundle: AgentBundle, *, track: str, problem: Dict[str, Any]) -> OrchestratorResult:
    prompt = f"""
Generate L3 variant for track={track}.
Examiner leads.

Problem:
{json.dumps(problem, ensure_ascii=False)}

Return FINAL_JSON schema:
{{
  "l3_variant_prompt":"text only",
  "variant_skill_tag":"one short tag",
  "success_criteria":["...","..."]
}}
""".strip()
    return run_group_stage(bundle, stage="l3", prompt=prompt)


def variant_grade(
    bundle: AgentBundle,
    *,
    track: str,
    problem: Dict[str, Any],
    l3_pack: Dict[str, Any],
    user_answer: str,
) -> OrchestratorResult:
    prompt = f"""
Grade the learner's L3 variant response for track={track}.

Problem:
{json.dumps(problem, ensure_ascii=False)}

L3 pack (prompt/criteria):
{json.dumps(l3_pack, ensure_ascii=False)}

User answer:
{user_answer}

Tutor leads; Reviewer can add 1 minimal fix; Motivator adds 1 line if user seems stuck.

Return FINAL_JSON schema:
{{
  "feedback":"短评：好在哪/缺哪",
  "minimal_fix":"最小补强建议",
  "tags":["..."],
  "next_check_question":"..."
}}
""".strip()
    return run_group_stage(bundle, stage="concept", prompt=prompt)


def review_coding(
    bundle: AgentBundle,
    *,
    problem: Dict[str, Any],
    user_code: str,
    test_result: Dict[str, Any],
    signals: Dict[str, Any],
) -> OrchestratorResult:
    prompt = f"""
Review a Coding attempt.
Reviewer leads, Motivator adds 1 line + adjustment suggestion.

Problem:
{json.dumps(problem, ensure_ascii=False)}

User code:
{user_code}

Local test_result (ground truth):
{json.dumps(test_result, ensure_ascii=False)}

Signals:
{json.dumps(signals, ensure_ascii=False)}

Return FINAL_JSON schema:
{{
  "review": {{
    "score": 0-10,
    "verdict": "correct|partial|wrong|error",
    "step_feedback":[{{"step":"...","comment":"..."}}],
    "minimal_fix":"do NOT paste full final code",
    "tags":["..."],
    "next_check_question":"..."
  }},
  "motivation": {{
    "tone":"...",
    "message":"one coachy line",
    "adjust": {{"scaffold_delta": -1|0|1, "hint_policy_delta": -1|0|1}}
  }}
}}
""".strip()
    return run_group_stage(bundle, stage="review", prompt=prompt)


def review_calculus(
    bundle: AgentBundle,
    *,
    problem: Dict[str, Any],
    user_work: str,
    signals: Dict[str, Any],
) -> OrchestratorResult:
    prompt = f"""
Review a Calculus attempt using the rubric.
Reviewer leads, Motivator adds 1 line.

Problem (includes rubric):
{json.dumps(problem, ensure_ascii=False)}

Student work (already transcribed if from image):
{user_work}

Signals:
{json.dumps(signals, ensure_ascii=False)}

Return FINAL_JSON schema:
{{
  "review": {{
    "score": 0-10,
    "verdict":"correct|partial|wrong|unreadable",
    "step_feedback":[{{"step_id":"s1","points_awarded":2,"comment":"...","tags":["..."]}}],
    "minimal_fix":"最小修正提示",
    "tags":["..."],
    "next_check_question":"..."
  }},
  "motivation": {{
    "tone":"...",
    "message":"one coachy line",
    "adjust": {{"scaffold_delta": -1|0|1, "hint_policy_delta": -1|0|1}}
  }}
}}
""".strip()
    return run_group_stage(bundle, stage="review", prompt=prompt)


def crystal(
    bundle: AgentBundle,
    *,
    track: str,
    problem: Dict[str, Any],
    session_summary: Dict[str, Any],
) -> OrchestratorResult:
    prompt = f"""
Create a Crystal card for track={track}.
Scribe leads; Planner adds one "tomorrow review安排" line.

Problem:
{json.dumps(problem, ensure_ascii=False)}

Session summary:
{json.dumps(session_summary, ensure_ascii=False)}

Return FINAL_JSON schema:
{{
  "core_pattern":"one short pattern",
  "common_pitfall":"one common pitfall",
  "trigger":"one trigger phrase",
  "review_plan":"tomorrow plan in 1-2 lines",
  "share_card_text":"short shareable card text"
}}
""".strip()
    return run_group_stage(bundle, stage="crystal", prompt=prompt)

