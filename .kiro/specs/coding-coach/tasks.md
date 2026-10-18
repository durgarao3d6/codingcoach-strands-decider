# CodingCoach — Tasks

## ✅ Milestone 1 — Foundation (done)
- [x] Write AGENT.md with use case, pitch, features, decision description
- [x] Implement `decision.py`: `LearnerStateClassifier`, `TeachingDecision`, `QUESTIONS`, `PATTERN_TAG`
- [x] Implement `tools.py`: `get_concept`, `generate_challenge`, `check_answer`
- [x] Implement `agent.py`: `HackathonAgent` with session state and classifier wiring
- [x] Write `eval_cases.jsonl`: 24 cases, 12 tune / 12 test, all 6 states covered
- [x] Write `demo_script.yaml`: 5-turn Socratic demo
- [x] Write `features.yaml`
- [x] `./kit test` — 38 passed
- [x] `./kit run` — end-to-end conversation working

## ✅ Milestone 2 — Benchmark (done)
- [x] `./kit bench --split tune` — ran 3 times, tuned question wording
- [x] Review results — 87.5% accuracy, 100% accurate when confident, 4.2x faster than LLM
- [x] `./kit bench --split test` — 87.5% accuracy, 100% when confident, 4.1x faster, $0.035/1k

## 🔴 Milestone 3 — Deploy
- [x] `.\kit.cmd bench --split test` — locked in
- [ ] `.\kit.cmd tools install deploy --yes` — install AgentCore CLI
- [ ] Set up AWS credentials: `.\kit.cmd aws-login`
- [ ] Enable Amazon Nova Pro in Bedrock → Model access (us-east-1)
- [ ] `.\kit.cmd deploy`
- [ ] `.\kit.cmd invoke "What is recursion?"` — prove it answers from AWS

## ✅ Milestone 4 — Video (done)
- [x] `.\kit.cmd video` — `submission/video/demo.mp4` generated (draft, local agent)
- [x] Narration generated — all 8 sections, real bench numbers
- [ ] Re-record with `.\kit.cmd video --target agentcore` after deploy (final submission video)

## 🔴 Milestone 5 — Article
- [ ] `.\kit.cmd article` — generate draft
- [ ] Edit to your own words, check all numbers match bench results
- [ ] Publish on AWS Builder Center with tags `#strands-decider-2b` and `#policy`

## 🔴 Milestone 6 — Final video (needs deploy first)
- [ ] `.\kit.cmd video --target agentcore` — re-record against deployed Bedrock agent
- [ ] Upload to YouTube or Vimeo (public, no music, no third-party logos)

## 🔴 Milestone 7 — Publish and submit
- [ ] `.\kit.cmd readme` — generate README
- [ ] `.\kit.cmd check` — fix all FAILs
- [ ] `.\kit.cmd publish <repo>` — create public GitHub repo
- [ ] Submit: repo URL + article URL + video URL before 23 Oct 2026 11:59 p.m. PT
- [ ] `.\kit.cmd destroy` after judging
