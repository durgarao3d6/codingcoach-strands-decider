# CodingCoach — Requirements

## Problem
Learners lose interest and feel like they're not retaining anything when AI assistants just dump
explanations. Reading an answer feels like learning, but the knowledge doesn't stick.

## Users
Developers learning to code — beginners to intermediate — who want to actually understand
concepts, not just get answers.

## Core requirement
The agent must never give a full explanation unprompted. Every response is shaped by where the
learner is right now, determined by Strands Decider 2B before the LLM responds.

## Functional requirements

### R1 — Learner state classification (the Strands Decider 2B decision)
Before every response, classify the learner's message into one of:
- `exploring` — asking about a concept for the first time
- `attempting` — sharing code or a partial answer
- `stuck` — has tried, explicitly lost
- `demonstrating_understanding` — showing correct reasoning
- `off_topic` — unrelated to coding
- `clarification_needed` — too ambiguous to act on

Return a confidence score. Below 0.55 confidence → ask a clarifying question regardless of
classification.

### R2 — Teaching actions mapped from state
| State | Default action |
|---|---|
| exploring | ask_question (diagnostic — what do you already know?) |
| attempting | check_answer |
| stuck | give_hint (smallest useful nudge) |
| demonstrating_understanding | generate_challenge (go deeper) |
| off_topic | redirect |
| clarification_needed | clarify |

Override: if `needs_direct_explanation` is true (learner explicitly asked, or 3+ failed
attempts), switch to `explain_concept` instead.

### R3 — Tools
- `get_concept(concept, language, level)` — structured explanation with definition, intuition,
  example, prerequisites, misconceptions
- `generate_challenge(concept, difficulty, language, level, known_misconceptions)` — exercise
  with hints and a learning objective
- `check_answer(challenge_id, learner_answer, ...)` — evaluate attempt, name what's right first,
  identify misconception, suggest next step. No code execution of untrusted input.

### R4 — Session state
Per session, track: topic, attempts, mastery (unknown / developing / demonstrated), current
challenge id, hints given. Keep history separate from structured state. Design so a database can
be swapped in later.

### R5 — Deployment
Runs on Amazon Bedrock AgentCore Runtime. LLM via Strands Agents SDK (never direct boto3).
Decider via the hosted API in the deployed version.

## Non-functional requirements
- Decider call adds < 2 s on the hosted API (measured, not estimated)
- No code execution of untrusted learner input in check_answer
- No secrets in code or docs
- Kit credit line in README, article footer, demo UI
