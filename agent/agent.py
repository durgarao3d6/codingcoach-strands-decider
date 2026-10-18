"""CodingCoach: an adaptive Socratic coding tutor.

Strands Decider 2B classifies every learner message before the LLM responds,
choosing the right teaching action (ask, hint, explain, challenge, check, redirect).

    from agent.agent import HackathonAgent
    out = HackathonAgent().chat("What is recursion?")
    out["reply"], out["decisions"]
"""

from __future__ import annotations

import time
from typing import Any

from strands import Agent

from decider_kit import Decider
from decider_kit.llm import agent_model, default_model_id, strip_thinking

from .decision import LearnerStateClassifier
from .tools import TOOLS

NAME = "CodingCoach"

_BASE_SYSTEM = """You are CodingCoach, a patient Socratic coding tutor. Your goal is genuine understanding, not just answers.

Rules:
- Follow the TEACHING DIRECTIVE at the end of this prompt exactly.
- Never give the full solution unless the directive says to explain directly.
- When checking an answer, name what is correct before saying what is wrong.
- Keep responses concise — one question or one hint at a time.
- Use the learner's language and level.
- If asked to generate a challenge, call generate_challenge. If asked to explain a concept, call get_concept. If checking code, call check_answer.
"""


class HackathonAgent:
    """One session per session_id. The decider runs before each LLM call."""

    def __init__(
        self,
        decider: Decider | None = None,
        model_id: str | None = None,
        eager: bool | None = None,  # unused for this agent; kept for contract compatibility
    ):
        self.decider = decider or Decider()
        self.model_id = model_id or default_model_id()
        self.classifier = LearnerStateClassifier(self.decider)
        # session_id → {"history": [...], "learner_state": {...}}
        self._sessions: dict[str, dict[str, Any]] = {}

    def _get_session(self, session_id: str) -> dict[str, Any]:
        if session_id not in self._sessions:
            self._sessions[session_id] = {
                "history": [],
                "learner_state": {
                    "topic": None,
                    "attempts": 0,
                    "mastery": "unknown",
                    "current_challenge_id": None,
                    "hints_given": 0,
                },
            }
        return self._sessions[session_id]

    def chat(
        self,
        message: str,
        session_id: str = "default",
        images: list[Any] | None = None,
    ) -> dict[str, Any]:
        session = self._get_session(session_id)
        history: list[dict] = session["history"]
        learner_state: dict = session["learner_state"]

        t0 = time.perf_counter()

        # 1. Classify the learner message with Strands Decider 2B
        td = self.classifier.classify(message, history, learner_state)

        # 2. Update lightweight learner state from the classification
        if td.learning_state == "attempting":
            learner_state["attempts"] = learner_state.get("attempts", 0) + 1
        if td.learning_state == "demonstrating_understanding":
            learner_state["mastery"] = "demonstrated"
        if td.teaching_action == "give_hint":
            learner_state["hints_given"] = learner_state.get("hints_given", 0) + 1

        # 3. Build the system prompt with the teaching directive injected
        system_prompt = _BASE_SYSTEM + "\n\n" + td.as_instruction()

        # 4. Build a fresh Strands Agent with the updated directive
        agent = Agent(
            model=agent_model(self.model_id),
            system_prompt=system_prompt,
            tools=TOOLS,
            callback_handler=None,
        )

        # 5. Replay history so the agent has context
        for turn in history[-10:]:  # keep last 5 exchanges
            agent.messages.append({"role": turn["role"], "content": [{"text": turn["content"]}]})

        # 6. Call the agent
        result = agent(message)
        reply = strip_thinking(str(result))

        # 7. Update history
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": reply})

        return {
            "reply": reply,
            "decisions": self.classifier.log[-1:],  # one decision per turn
            "model_id": self.model_id,
            "latency_ms": round((time.perf_counter() - t0) * 1000),
            "agent": NAME,
            "eager": False,
        }


if __name__ == "__main__":
    import json
    import sys

    a = HackathonAgent()
    msgs = sys.argv[1:] or [
        "What is recursion?",
        "I think a function calls itself.",
        "Maybe when n equals zero it stops?",
    ]
    for msg in msgs:
        print(f"\nUser: {msg}")
        out = a.chat(msg)
        print(f"Coach: {out['reply']}")
        print(f"[decision: {out['decisions']}]")
