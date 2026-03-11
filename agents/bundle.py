"""AutoGen agent bundle and configuration"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

# ---------------------------------------------------------------------------
# Monkey-patch openai.OpenAI to route calls through ichat gateway.
# This must happen BEFORE autogen imports openai internally.
# ---------------------------------------------------------------------------
from agents import gpt_client as _gpt

import openai as _openai_pkg


class _PatchedCompletions:
    """Intercept chat.completions.create and route to ichat."""

    def create(self, *, model: str = "gpt-4o", messages: list, **kwargs):
        text, raw = _gpt.ichat_chat_completions(
            model=model,
            messages=messages,
            max_tokens=kwargs.get("max_tokens", 1600),
            temperature=kwargs.get("temperature", 0.4),
        )
        return _FakeCompletion(text, model)


class _FakeCompletion:
    def __init__(self, text: str, model: str):
        self.choices = [_FakeChoice(text)]
        self.model = model
        self.usage = _FakeUsage()

    def model_dump(self):
        return {"choices": [{"message": {"content": self.choices[0].message.content}}], "model": self.model}


class _FakeChoice:
    def __init__(self, text: str):
        self.message = _FakeMessage(text)
        self.finish_reason = "stop"


class _FakeMessage:
    def __init__(self, text: str):
        self.content = text
        self.function_call = None
        self.tool_calls = None
        self.role = "assistant"


class _FakeUsage:
    prompt_tokens = 0
    completion_tokens = 0
    total_tokens = 0


class _PatchedChat:
    def __init__(self):
        self.completions = _PatchedCompletions()


class _PatchedOpenAI:
    """Drop-in replacement for openai.OpenAI that uses ichat."""

    def __init__(self, *args, **kwargs):
        self.chat = _PatchedChat()


# Apply the patch
_openai_pkg.OpenAI = _PatchedOpenAI
_openai_pkg.AzureOpenAI = _PatchedOpenAI

# ---------------------------------------------------------------------------
# Now safe to import autogen
# ---------------------------------------------------------------------------
from autogen import AssistantAgent, GroupChat, GroupChatManager, UserProxyAgent

MODEL = "gpt-4o"


@dataclass(frozen=True)
class AgentBundle:
    planner: AssistantAgent
    tutor: AssistantAgent
    examiner: AssistantAgent
    reviewer: AssistantAgent
    motivator: AssistantAgent
    scribe: AssistantAgent
    manager: GroupChatManager
    user: UserProxyAgent


def default_llm_config() -> Dict[str, Any]:
    return {
        "config_list": [{"model": MODEL}],
        "temperature": 0.4,
    }


def _json_only_contract(extra: str = "") -> str:
    return (
        "You must output STRICT JSON when asked for 'FINAL_JSON'. "
        "No markdown fences, no commentary, no trailing commas.\n"
        + extra
    )


def build_agents(llm_config: Optional[Dict[str, Any]] = None) -> Tuple[AgentBundle, Dict[str, Any]]:
    llm_config = llm_config or default_llm_config()

    planner = AssistantAgent(
        name="Planner",
        description="Plans Daily Drop; selects today's tasks with a crisp, coachy reason.",
        system_message=(
            "You are Planner in Ascend Flow. You pick tasks that maximize learning transfer with minimal friction. "
            "Write short, coach-style lines. Prefer concrete goals.\n" + _json_only_contract()
        ),
        llm_config=llm_config,
    )
    tutor = AssistantAgent(
        name="Tutor",
        description="Feynman-style teacher for Concept Check; explain briefly, ask one sharp check question, then grade the user's answer.",
        system_message=(
            "You are Tutor in Ascend Flow. Your job is Concept Check.\n"
            "Rules: explanation <= 120 Chinese characters; 1 check question; expected_points as a short bullet list; "
            "feedback should be direct, kind, high-density. If user is confused, give an alternate explanation style.\n"
            + _json_only_contract()
        ),
        llm_config=llm_config,
    )
    examiner = AssistantAgent(
        name="Examiner",
        description="Creates scaffolded practice: L1 cloze + L3 variant challenge.",
        system_message=(
            "You are Examiner in Ascend Flow. Generate L1 (fill-in / cloze) and L3 (variant challenge). "
            "Make L1 minimal but decisive. Provide answer key.\n" + _json_only_contract()
        ),
        llm_config=llm_config,
    )
    reviewer = AssistantAgent(
        name="Reviewer",
        description="Process-oriented grader; gives minimal-fix hints and tags.",
        system_message=(
            "You are Reviewer in Ascend Flow. Grade with a rubric-like step breakdown and tags.\n"
            "Rules: do NOT paste full final solution code. For coding, provide minimal fix hint based on local tests. "
            "For calculus, score by rubric steps and pinpoint wrong step(s). "
            "Always propose one next_check_question.\n" + _json_only_contract()
        ),
        llm_config=llm_config,
    )
    motivator = AssistantAgent(
        name="Motivator",
        description="Emotion coach; generates one coachy line and adjustment suggestions.",
        system_message=(
            "You are Motivator in Ascend Flow. Your job: emotion regulation + pacing.\n"
            "Input signals may include: elapsed_minutes, fail_count, hints_used, scaffold_level.\n"
            "Output tone/message and a small adjustment policy.\n" + _json_only_contract()
        ),
        llm_config=llm_config,
    )
    scribe = AssistantAgent(
        name="Scribe",
        description="Creates Crystal card: pattern, pitfalls, triggers, review plan.",
        system_message=(
            "You are Scribe in Ascend Flow. Your output becomes a Crystal card.\n"
            "Write crisp, coachy, memorable content. No long paragraphs.\n" + _json_only_contract()
        ),
        llm_config=llm_config,
    )

    manager = GroupChatManager(
        groupchat=GroupChat(
            agents=[planner, tutor, examiner, reviewer, motivator, scribe],
            messages=[],
            max_round=12,
        ),
        name="Manager",
        system_message=(
            "You are the GroupChatManager for Ascend Flow. You orchestrate the team.\n"
            "When the user asks for FINAL_JSON, you MUST output ONLY valid JSON.\n"
            "You may ask ONE clarifying question if absolutely required; otherwise proceed.\n"
            "Keep the team on-task: Planner→Daily Drop, Tutor→Concept, Examiner→L1/L3, Reviewer→grading, "
            "Motivator→coaching, Scribe→Crystal.\n"
            + _json_only_contract(
                "If multiple agents propose content, you unify into one clean JSON schema requested by the prompt."
            )
        ),
        llm_config=llm_config,
    )

    user = UserProxyAgent(
        name="User",
        system_message="You are the learner. You provide short answers and submissions.",
        human_input_mode="NEVER",
        code_execution_config=False,
    )

    bundle = AgentBundle(
        planner=planner,
        tutor=tutor,
        examiner=examiner,
        reviewer=reviewer,
        motivator=motivator,
        scribe=scribe,
        manager=manager,
        user=user,
    )
    return bundle, llm_config


def reset_groupchat(bundle: AgentBundle) -> None:
    bundle.manager.groupchat.messages.clear()
    for a in [bundle.planner, bundle.tutor, bundle.examiner, bundle.reviewer, bundle.motivator, bundle.scribe, bundle.manager]:
        try:
            a.reset()
        except Exception:
            pass


def apply_allowed_transitions(bundle: AgentBundle, *, stage: str) -> None:
    """Best-effort: configure allowed speaker transitions if supported."""
    stage = stage.lower().strip()
    agents = {
        "Planner": bundle.planner,
        "Tutor": bundle.tutor,
        "Examiner": bundle.examiner,
        "Reviewer": bundle.reviewer,
        "Motivator": bundle.motivator,
        "Scribe": bundle.scribe,
    }

    transitions_map = {
        "daily_drop": {
            agents["Planner"]: [agents["Motivator"], agents["Planner"], agents["Scribe"]],
            agents["Motivator"]: [agents["Planner"]],
            agents["Scribe"]: [agents["Planner"]],
            agents["Tutor"]: [agents["Planner"]],
            agents["Examiner"]: [agents["Planner"]],
            agents["Reviewer"]: [agents["Planner"]],
        },
        "concept": {
            agents["Tutor"]: [agents["Reviewer"], agents["Motivator"], agents["Tutor"]],
            agents["Reviewer"]: [agents["Tutor"], agents["Motivator"]],
            agents["Motivator"]: [agents["Tutor"]],
            agents["Planner"]: [agents["Tutor"]],
            agents["Examiner"]: [agents["Tutor"]],
            agents["Scribe"]: [agents["Tutor"]],
        },
        "l1": {
            agents["Examiner"]: [agents["Reviewer"], agents["Motivator"], agents["Examiner"]],
            agents["Reviewer"]: [agents["Examiner"]],
            agents["Motivator"]: [agents["Examiner"]],
            agents["Tutor"]: [agents["Examiner"]],
            agents["Planner"]: [agents["Examiner"]],
            agents["Scribe"]: [agents["Examiner"]],
        },
        "review": {
            agents["Reviewer"]: [agents["Motivator"], agents["Reviewer"]],
            agents["Motivator"]: [agents["Reviewer"]],
            agents["Tutor"]: [agents["Reviewer"]],
            agents["Examiner"]: [agents["Reviewer"]],
            agents["Planner"]: [agents["Reviewer"]],
            agents["Scribe"]: [agents["Reviewer"]],
        },
        "crystal": {
            agents["Scribe"]: [agents["Planner"], agents["Scribe"]],
            agents["Planner"]: [agents["Scribe"]],
            agents["Motivator"]: [agents["Scribe"]],
            agents["Tutor"]: [agents["Scribe"]],
            agents["Examiner"]: [agents["Scribe"]],
            agents["Reviewer"]: [agents["Scribe"]],
        },
    }
    transitions_map["l3"] = transitions_map["l1"]

    allowed = transitions_map.get(stage)
    if not allowed:
        return

    gc = bundle.manager.groupchat
    try:
        gc.allowed_or_disallowed_speaker_transitions = allowed
        gc.speaker_transitions_type = "allowed"
    except Exception:
        pass

