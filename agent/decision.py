"""REUSABLE DECISION PATTERN: learner-state policy classification  (#policy)

What it does
    Before the coding tutor responds to a learner, Strands Decider 2B reads the conversation
    and classifies the learner's current state:

    - exploring: asking about a new concept they haven't tried yet
    - attempting: actively working on a problem (sharing code or a partial answer)
    - stuck: has tried and hit a wall — explicitly says so or has made multiple failed attempts
    - demonstrating_understanding: showing they understand — correct reasoning or working code
    - off_topic: not related to coding or the current learning session
    - clarification_needed: too ambiguous to classify confidently

    The classification drives the teaching action (ask_question, give_hint, explain_concept,
    generate_challenge, check_answer, redirect, clarify). Low-confidence responses fall back to
    a clarifying question rather than guessing wrong and either spoiling the answer or being
    unhelpfully cryptic.

Typed questions and options
    `learning_state` (choice): six states, each with a one-line definition; see QUESTIONS.
    `needs_direct_explanation` (noul): override — has the learner explicitly asked for a direct
    answer, or struggled so many times that withholding is no longer helpful?

Wiring
    `LearnerStateClassifier` is called once at the start of `HackathonAgent.chat`, before the
    Strands Agent runs. It returns a `TeachingDecision` that is injected into the system prompt
    so the LLM knows exactly how to respond.

        classifier = LearnerStateClassifier(decider)
        td = classifier.classify(message, conversation_history, learner_state)
        # td.teaching_action, td.learning_state, td.confident, td.decider_ms

How to reuse it
    Copy this file, rewrite the six states for your domain (e.g. customer intent in a support
    agent, risk level in a compliance checker), and adjust the action mapping in
    `LearnerStateClassifier.decide()`. The threshold logic (confidence < LOW_CONF → clarify)
    stays the same.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from decider_kit import Decider

PATTERN_TAG = "#policy"

LOW_CONF = 0.55  # below this confidence, ask a clarifying question instead of guessing

# Learning states the decider chooses between
LEARNING_STATES = {
    "exploring": "the learner asks a clear, specific question about a named concept or topic they have not tried yet — for example 'what is recursion?' or 'how does a for loop work?' — and the message contains enough context to answer without asking back",
    "attempting": "the learner shares code or a partial written answer and wants it checked — the message contains an attempt (code block, pseudocode, or incomplete reasoning) but the learner has NOT yet explained whether it works or why",
    "stuck": "the learner says they cannot figure something out after trying — explicit confusion words: 'I don't get it', 'I'm stuck', 'I still don't understand', 'I've tried and I can't', 'I don't know why'; the message may or may not include code",
    "demonstrating_understanding": "the learner explains in their own words WHY something works — they articulate the mechanism, the cause-and-effect, or the insight ('oh I see, the base case stops infinite recursion because...') rather than just submitting code or asking a question",
    "off_topic": "the message is clearly not about coding, programming, or the current lesson — weather, personal questions, entertainment, or unrelated subjects",
    "clarification_needed": "the message is a single word or very short phrase with no coding topic mentioned — such as 'help', 'hello', 'I need help', or 'it's not working' — where it is impossible to know what the learner wants without asking first",
}

QUESTIONS = {
    "learning_state": Decider.choice(
        "What is the learner's current state in this message?",
        LEARNING_STATES,
    ),
    "needs_direct_explanation": Decider.noul(
        "Has the learner explicitly asked for a direct answer or explanation, or have they struggled with the same concept unsuccessfully multiple times?",
        {
            "true": "the learner said 'just tell me', 'explain it', 'I give up', or has made three or more failed attempts at the same concept",
            "false": "the learner has not asked for a direct answer and has not exhausted their attempts",
        },
    ),
}

# Map learning state → default teaching action
_ACTION_MAP = {
    "exploring": "ask_question",           # don't dump — ask what they already know
    "attempting": "check_answer",          # they shared work — evaluate it
    "stuck": "give_hint",                  # they tried — give the smallest useful nudge
    "demonstrating_understanding": "generate_challenge",  # they got it — go deeper
    "off_topic": "redirect",
    "clarification_needed": "clarify",
}


@dataclass
class TeachingDecision:
    learning_state: str
    teaching_action: str
    confident: bool
    decider_ms: int
    needs_direct: bool
    answers: dict[str, Any] = field(repr=False, default_factory=dict)

    def as_instruction(self) -> str:
        """Short directive injected into the system prompt before the LLM responds."""
        action_text = {
            "ask_question": "Ask the learner a diagnostic question to reveal what they already know. Do NOT explain the concept yet.",
            "check_answer": "Evaluate the learner's attempt. Name what is correct first, then identify the specific gap. Do NOT give the full solution.",
            "give_hint": "Give one small hint that moves the learner forward without revealing the answer. Ask them to try again.",
            "generate_challenge": "The learner demonstrated understanding. Offer a small challenge that goes one level deeper.",
            "explain_concept": "Give a clear, concise explanation. Use a concrete example. Then ask a follow-up question.",
            "redirect": "Politely note that this is outside the coding lesson and guide them back to the topic.",
            "clarify": "Ask a short clarifying question to understand what the learner needs before responding.",
            "increase_difficulty": "The learner is ready for more. Increase the challenge.",
            "reduce_difficulty": "The learner is struggling. Simplify the concept or break it into smaller steps.",
        }.get(self.teaching_action, "Respond helpfully.")

        if self.needs_direct and self.teaching_action not in ("redirect", "clarify"):
            action_text = "The learner has explicitly asked for an explanation or has struggled many times. Give a clear, direct explanation now. Then offer a challenge."

        if not self.confident:
            action_text = "You are not sure what the learner needs. Ask a short clarifying question before doing anything else."

        return f"[TEACHING DIRECTIVE — learning state: {self.learning_state}]\n{action_text}"


class LearnerStateClassifier:
    """Classify each learner message and return a TeachingDecision.

    Call once per turn before building the Strands Agent response.
    """

    def __init__(self, decider: Decider):
        self.decider = decider
        self.log: list[dict[str, Any]] = []

    def classify(
        self,
        message: str,
        history: list[dict[str, str]],
        learner_state: dict[str, Any] | None = None,
    ) -> TeachingDecision:
        """Read the message + conversation history and return a TeachingDecision."""
        state_text = self._build_state(message, history, learner_state)
        answers = self.decider.ask(state_text, QUESTIONS)
        td = self._decide(answers)
        self.log.append({
            "pattern": PATTERN_TAG,
            "learning_state": td.learning_state,
            "teaching_action": td.teaching_action,
            "confident": td.confident,
            "needs_direct": td.needs_direct,
            "decider_ms": td.decider_ms,
        })
        return td

    def _build_state(
        self,
        message: str,
        history: list[dict[str, str]],
        learner_state: dict[str, Any] | None,
    ) -> str:
        lines = ["A coding tutor conversation. Classify the learner's latest message.\n"]
        if learner_state:
            topic = learner_state.get("topic", "unknown")
            attempts = learner_state.get("attempts", 0)
            mastery = learner_state.get("mastery", "unknown")
            lines.append(f"--- LEARNER STATE ---\nTopic: {topic}  Attempts: {attempts}  Mastery: {mastery}\n")
        if history:
            lines.append("--- CONVERSATION HISTORY ---")
            for turn in history[-6:]:  # last 3 exchanges
                lines.append(f"{turn['role'].capitalize()}: {turn['content']}")
            lines.append("")
        lines.append(f"--- LATEST LEARNER MESSAGE ---\n{message}")
        return "\n".join(lines)

    def _decide(self, answers: dict) -> TeachingDecision:
        state_ans = answers["learning_state"]
        direct_ans = answers["needs_direct_explanation"]

        learning_state = state_ans.label or "clarification_needed"
        confidence = state_ans.confidence or 0.0
        confident = confidence >= LOW_CONF
        needs_direct = direct_ans.p_yes is not None and direct_ans.p_yes >= 0.5

        if not confident:
            teaching_action = "clarify"
        elif needs_direct and learning_state not in ("off_topic", "clarification_needed"):
            teaching_action = "explain_concept"
        else:
            teaching_action = _ACTION_MAP.get(learning_state, "clarify")

        return TeachingDecision(
            learning_state=learning_state,
            teaching_action=teaching_action,
            confident=confident,
            decider_ms=round(self.decider.last_latency_ms or 0),
            needs_direct=needs_direct,
            answers=answers,
        )
