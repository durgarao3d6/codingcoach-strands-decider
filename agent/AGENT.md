# CodingCoach — Adaptive Socratic Coding Tutor

- **Pitch:** an AI coding tutor that never dumps answers — it reads where you are and asks, hints, or explains just enough.
- **Who it is for:** developers learning to code who lose interest or feel like they're not retaining anything when a regular AI just explains everything.
- **Features:**
  - Socratic questioning: asks what you already know before explaining anything
  - Adaptive hints: gives the smallest nudge that moves you forward
  - Challenge generation: creates exercises at your current level
  - Answer checking: tells you what's right before saying what's wrong
  - Deployed on Amazon Bedrock AgentCore Runtime
- **The decision handed to Strands Decider 2B:** before the agent responds, classify the learner's message into a learning state (`exploring`, `attempting`, `stuck`, `demonstrating_understanding`, `off_topic`, `clarification_needed`) and pick the right teaching action. (`#policy`)
- **Why a decision model:** this classification runs on every single message — it must be fast, cheap, and return a confidence the code can branch on (low confidence → ask a clarifying question instead of guessing).
- **Amazon Bedrock:** the conversation and tool use (Amazon Nova Pro by default).
