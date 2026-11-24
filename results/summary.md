# traces-eval results

Sample: nvidia/Open-SWE-Traces v2.0, source scale-swe, reasoning xhigh, model Qwen3.8-Flash-Next.
60 tasks attempted by all 5 agents (30 mixed, 20 nobody solved, 10 everybody solved) → 300 runs, 163 failures.

## 1. Do agents know they failed? (step 6, AI judge on the final message)

| Agent | Failed runs | Claimed success | 95% CI | Claimed they verified it |
|---|---|---|---|---|
| Claude Code | 32 | 32 (100%) | 89%–100% | 32 (100%) |
| OpenCode | 33 | 32 (97%) | 85%–99% | 29 (88%) |
| OpenHands | 32 | 26 (81%) | 65%–91% | 25 (78%) |
| SWE-agent | 31 | 29 (94%) | 79%–98% | 26 (84%) |
| mini-SWE-agent | 35 | 34 (97%) | 85%–99% | 33 (94%) |
| **All** | 163 | **153 (94%)** | 89%–97% | |

Solved runs claimed success 127/137 (93%) of the time, so a success claim barely separates solved from failed runs.

## 2. Why do they fail? (step 8, rubric v1, grader A on all 163 failures)

| Type | All agents | 95% CI | Claude Code | OpenCode | OpenHands | SWE-agent | mini-SWE-agent |
|---|---|---|---|---|---|---|---|
| 1. unwired code | 8 (5%) | 3%–9% | 2 | 0 | 2 | 3 | 1 |
| 2. missed part of request | 30 (18%) | 13%–25% | 5 | 7 | 7 | 9 | 2 |
| 3. wrong location | 10 (6%) | 3%–11% | 2 | 2 | 1 | 1 | 4 |
| 4. broke existing behaviour | 17 (10%) | 7%–16% | 2 | 6 | 3 | 3 | 3 |
| 5. wrong assumption | 17 (10%) | 7%–16% | 2 | 3 | 5 | 3 | 4 |
| 6. hidden-test mismatch | 67 (41%) | 34%–49% | 15 | 13 | 13 | 10 | 16 |
| 7. looks correct | 8 (5%) | 3%–9% | 2 | 1 | 1 | 1 | 3 |
| 8. other / unclear | 6 (4%) | 2%–8% | 2 | 1 | 0 | 1 | 2 |

- Agent mistakes (types 1–5): **82 (50%)**
- Task or grader problems (types 6–7): **75 (46%)**

## 3. Effort: messages per run

| Agent | Solved (median) | Failed (median) |
|---|---|---|
| Claude Code | 78 | 89 |
| OpenCode | 44 | 54 |
| OpenHands | 67 | 75 |
| SWE-agent | 77 | 95 |
| mini-SWE-agent | 70 | 91 |
