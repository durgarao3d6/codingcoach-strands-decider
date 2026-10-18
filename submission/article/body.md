# CodingCoach: A Socratic AI Tutor That Decides Before It Speaks

By [Your Name]

When I started learning to code with AI assistants, something felt off. I would ask a question, get a detailed explanation, read it — and feel like I understood. Then I would try to write the code myself and realise I had retained almost nothing. The AI had done all the thinking for me.

CodingCoach is my attempt to fix that. It is a coding tutor that never dumps an answer until you have actually tried. Before every response, Strands Decider 2B reads your message and decides what kind of help you actually need right now — not what would be easiest to give you.

## The project

CodingCoach is for developers learning to code who feel like AI assistants explain too much, too fast, and leave nothing for the learner to figure out. The tutor adapts to where you are in real time.

Ask "what is recursion?" and you will not get a textbook definition. You will get a question back: "What do you think happens when a function calls itself?" Share code with a bug and the tutor will tell you what you got right before pointing at the gap. Say "I give up, just explain it" after several failed attempts and it finally explains — because at that point, explaining is the right move.

Here is a short example of how a session goes:

> **Learner:** What is recursion?
>
> **CodingCoach:** Good question. Before I explain — what do you think happens when a function calls itself?
>
> **Learner:** I think it just keeps calling itself?
>
> **CodingCoach:** Exactly the right instinct. So what would stop it from going forever?
>
> **Learner:** Maybe when n equals zero?
>
> **CodingCoach:** Yes — that is called the base case. Now try writing a function that counts down from n to zero using that idea.

The tutor has four tools it can call: `get_concept` (structured explanation with examples and common mistakes), `generate_challenge` (an exercise at the right difficulty), `check_answer` (evaluates the learner's attempt, names what is correct first), and a fallback for off-topic requests.

< FIGURE 1 of 6: upload submission/article/img/demo.png here >
Alt text: The CodingCoach demo UI: the conversation on the left, the decider's decision panel on the right showing learning state, teaching action, confidence, and latency

## How I built it

CodingCoach is built on the Strands Agents SDK with Amazon Bedrock (Amazon Nova Pro) as the language model. The tools are Python functions decorated with `@tool` and registered with the Strands Agent. The agent runs on Amazon Bedrock AgentCore Runtime for the deployed version.

The build used the AWS User Group Madurai Strands Decider hackathon kit — Kiro with spec-driven development, the `decider_kit` library for the Strands Decider client and patterns, and the kit's benchmark and video tooling. The kit handled the scaffolding; the agent, the decision, and the tools are original to this project.

## The decision I handed to Strands Decider 2B

Every message a learner sends needs to be classified before the tutor responds. The wrong classification leads to the wrong response: explaining to someone who just needs a nudge, or asking a question to someone who has genuinely tried and is stuck. Getting this wrong consistently is exactly how AI tutors kill motivation.

Strands Decider 2B reads the message and the conversation history and answers two questions in a single forward pass:

```python
QUESTIONS = {
    "learning_state": Decider.choice(
        "What is the learner's current state in this message?",
        {
            "exploring": "the learner asks a clear, specific question about a named concept they have not tried yet",
            "attempting": "the learner shares code or a partial answer and wants it checked",
            "stuck": "the learner says they cannot figure something out after trying — explicit confusion words",
            "demonstrating_understanding": "the learner explains in their own words WHY something works",
            "off_topic": "the message is clearly not about coding or the current lesson",
            "clarification_needed": "the message is too short or ambiguous to act on without asking back",
        },
    ),
    "needs_direct_explanation": Decider.noul(
        "Has the learner explicitly asked for a direct answer, or struggled unsuccessfully multiple times?",
        {
            "true": "the learner said 'just tell me', 'I give up', or has made three or more failed attempts",
            "false": "the learner has not asked for a direct answer and has not exhausted their attempts",
        },
    ),
}
```

The classification maps directly to a teaching action: `exploring` → ask a diagnostic question; `attempting` → check the answer; `stuck` → give the smallest useful hint; `demonstrating_understanding` → offer a harder challenge. If `needs_direct_explanation` is true, the action overrides to explain directly — because at that point, more Socratic questioning is just frustrating.

When the decider's confidence is below 0.55, the action falls back to `clarify` — the tutor asks what the learner actually needs rather than guessing. This matters: a wrong classification at low confidence does more harm than a clarifying question.

< FIGURE 2 of 6: upload submission/article/img/architecture.png here >
Alt text: Architecture diagram: learner message → Strands Decider 2B classifies → teaching directive injected into system prompt → Strands Agent with tools → reply

## Measured results

I evaluated the decider on a held-out test split of 24 labelled decisions — 12 cases, two questions each — covering all six learning states, including near-miss cases like a learner sharing working code versus a learner explaining why it works.

| | Strands Decider 2B | LLM baseline (qwen3.5-4b) |
|---|---|---|
| Accuracy | 87.5% | 87.5% |
| Latency p50 per decision | 4,914 ms | 19,975 ms |
| Latency p95 | 5,480 ms | 20,658 ms |
| Cost per 1,000 decisions | $0.035 | $0.000 |
| Answered at confidence ≥ 0.7 | 42% | 96% |
| Accuracy when confident | **100%** | 87.0% |

The accuracy is the same — but the decider runs in about one quarter of the median time. That matters because this classification happens on every single message. Every second saved here is a second less the learner waits before the tutor responds.

The most interesting number is the last row. When the decider is confident (42% of decisions), it is 100% accurate. When it is not confident, it defers — the action falls back to `clarify`. The LLM baseline never defers; it always picks an answer, and is occasionally wrong. For a tutoring application where the wrong move can actively frustrate the learner, having a calibrated confidence score that the code can branch on is genuinely useful.

The main weakness: `demonstrating_understanding` and `stuck` are hard to separate at the boundary. A learner who shares partially correct reasoning and says "I think I get it?" is genuinely ambiguous — the decider often falls below the confidence threshold on these cases and defers correctly.

< FIGURE 3 of 6: upload submission/article/img/bench-accuracy.png here >
Alt text: Accuracy comparison: Strands Decider 2B vs LLM baseline on 24 labelled decisions

< FIGURE 4 of 6: upload submission/article/img/bench-latency.png here >
Alt text: Latency per decision: decider p50 4,914 ms vs LLM p50 19,975 ms

< FIGURE 5 of 6: upload submission/article/img/bench-cost.png here >
Alt text: Cost per 1,000 decisions: $0.035 for the decider vs $0 for a free hosted model

< FIGURE 6 of 6: upload submission/article/img/bench-confidence.png here >
Alt text: Accuracy at confidence threshold: the decider hits 100% accuracy on the cases it answers confidently

## The reusable decision pattern

The pattern lives in `agent/decision.py` and is labelled `#policy`. It classifies any incoming message into a set of named categories before the agent acts — the same shape works for customer intent in a support agent, content moderation, or triage in any domain where the right response depends on what the user actually means.

To reuse it: copy `decision.py`, replace the six `LEARNING_STATES` with your own categories and one-line definitions, adjust the action mapping in `_ACTION_MAP`, and wire the `LearnerStateClassifier` before your Strands Agent call. The confidence threshold and the low-confidence fallback stay the same.

```python
# Drop-in usage
classifier = LearnerStateClassifier(Decider())
td = classifier.classify(message, history, learner_state)
system_prompt = BASE_PROMPT + "\n\n" + td.as_instruction()
agent = Agent(model=..., system_prompt=system_prompt, tools=TOOLS)
```

## What I learned and what is next

The biggest lesson: writing sharp option descriptions for the decider is the whole job. The model is small and fast precisely because it does not generate text — it reads the descriptions you write and returns probabilities. Vague descriptions give vague results. The three tuning rounds on the bench were mostly rewording `attempting` vs `demonstrating_understanding` until the boundary was crisp enough for the model to act on.

What is next: adding AgentCore Memory so the tutor remembers which concepts a learner has struggled with across sessions. The decider would then also decide what is worth storing — a natural `#context-memory` extension of the same pattern.

---

Code: [repo link] · Video: [video link] · Tags: #strands-decider-2b #policy

Built with the AWS User Group Madurai Strands Decider hackathon kit
