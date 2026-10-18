# CodingCoach — Design

## Pattern
`#policy` — classify the learner's message before the LLM responds.

## Architecture

```
learner message
      │
      ▼
LearnerStateClassifier          ← Strands Decider 2B (one call, two questions)
  learning_state (choice/6)
  needs_direct_explanation (noul)
      │
      ▼
TeachingDecision.as_instruction()   ← maps state → teaching action → directive string
      │
      ▼
Strands Agent (system_prompt = base + directive)
  tools: get_concept, generate_challenge, check_answer
      │
      ▼
reply + decisions log
```

## Decider questions

Both questions are asked in one call (state encoded once, shared):

**learning_state** (choice, 6 options)
Each option has a one-line definition that is specific enough for the 2B model to distinguish
between "asking about a concept" and "sharing a partial attempt".

**needs_direct_explanation** (noul)
Catches the "I give up, just tell me" case and the repeated-failure case. Overrides the default
action to `explain_concept`.

## Key design decisions

**Directive injection, not tool routing**
The decider result is injected into the system prompt as a `[TEACHING DIRECTIVE]` block. This
means the LLM always knows the intended teaching move without needing another tool call or a
custom InterventionHandler. Simpler, and the directive is visible in the demo UI.

**Fresh Agent per turn, history replayed**
Strands Agent is stateless per construction. We replay the last 10 messages (5 exchanges) so the
LLM has context without unbounded memory growth. The structured learner state (attempts, mastery)
is maintained separately in Python.

**No code execution**
`check_answer` uses heuristic signal matching (key substrings in the learner's answer). This is
intentional — executing untrusted learner code in the main process is unsafe. The tool reports
`uncertain: true` when it can't reliably evaluate.

**Low-confidence fallback**
Below 0.55 confidence on `learning_state`, the teaching action is forced to `clarify` regardless
of the label. This is a hard rule in code, not a decider decision.

## File layout
```
agent/
  AGENT.md          use case description
  decision.py       LearnerStateClassifier, TeachingDecision, QUESTIONS, PATTERN_TAG
  tools.py          get_concept, generate_challenge, check_answer + concept/challenge data
  agent.py          HackathonAgent: session state, classifier call, Strands Agent
  eval_cases.jsonl  24 labelled cases (12 tune, 12 test)
  demo_script.yaml  5-turn Socratic demo
  features.yaml     AgentCore Memory/Gateway (both off for initial deploy)
```
