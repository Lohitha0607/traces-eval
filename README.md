# traces-eval

**Why do coding agents fail, and do they know they failed?**

An error analysis of 300 real coding-agent runs (5 agents, same model, same tasks), followed by Harbor tasks built from the most common agent mistakes.

## Headline results
- **Agents almost never admit failure.** In **94%** of failed runs (153/163, 95% CI 89–97%) the agent's final message still claimed the fix worked, and in 89% it claimed to have verified it. Solved runs claimed success 93% of the time, so a success claim says almost nothing about the outcome.
- **Almost half of the failures are not agent mistakes.** In **41%** of failures the hidden tests required names, exact values or files that the issue never stated (*hidden-test mismatch*); another 5% look correct. Agent mistakes (types 1–5) explain **50%**.
- **The real agent mistakes:** missed part of the request (18%), broke existing behaviour (10%), wrong assumption (10%), wrong location (6%), unwired code (5%).
- **When the task is clearly specified, the traps are avoided.** On our Harbor tasks built from those mistakes (each task text states everything the grader checks), all five agents (goose, pi, Prime Agent, mini-SWE-agent, OpenCode) passed every run (51/51), and their self-reported confidence matched the outcome. See [Half 2](#half-2-harbor-tasks-from-the-top-mistakes).

![False success](results/false_success.png)
![Failure types](results/failure_types.png)

## Data
- [nvidia/Open-SWE-Traces](https://huggingface.co/datasets/nvidia/Open-SWE-Traces) v2.0 (CC BY 4.0), source `scale-swe`, reasoning effort `xhigh`.
- All five agents run the **same model** (Qwen3.8-Flash-Next), so differences come from the agent design: Claude Code, OpenCode, OpenHands, SWE-agent, mini-SWE-agent.
- Sample: 60 tasks attempted by all five agents, stratified by how many agents solved them (30 mixed, 20 none, 10 all) with a fixed seed → **300 runs, 163 failures**.

## Method (Half 1)
| Step | What | Script / output |
|---|---|---|
| Index | light columns of every run, read straight from Hugging Face | `scripts/build_index.py` |
| Sample | shared tasks, stratified, fixed seed | `scripts/pick_sample.py` |
| Fetch | only the sampled rows, verified (trajectory id, not truncated) | `scripts/locate.py`, `offsets.py`, `fetch_rows.py` |
| Viewer | local HTML page per run, incl. the model's thinking | `scripts/make_viewer.py` |
| False success | an AI judge labels each final message (claims success / hedged / admits failure), blind to the outcome | `scripts/judge_claims.py` → `results/claims.jsonl` |
| Failure notes | an AI drafts one note per failed run (sees the reference patch) | `scripts/draft_notes.py` → `results/notes_draft.jsonl` |
| Spot check | 15 notes checked against the issue text and both patches: 7 correct, 5 partly, 2 unsure, 1 partly wrong | `results/spotcheck.json` |
| Rubric | 8 failure types built from the notes (not from preset labels) | `rubric.md` |
| Two graders | grader A (Claude, all 163, from the notes) and grader B (AI, from raw evidence, 77 usable labels) | `results/labels_*` |
| Agreement | 69% exact, Cohen's kappa 0.57; 75% agree on "agent mistake vs task/grader problem" | `results/agreement.txt` |
| Report | counts with Wilson 95% intervals and charts | `scripts/report.py` → `results/summary.md` |

## Half 2: Harbor tasks from the top mistakes
Three tasks, one per top agent-mistake type, each based on a real pattern from Half 1. Every task text states everything the hidden grader checks (lesson from the 41% hidden-test mismatch). Each task asks the agent to write `{"fixed": ..., "confidence": 0-100}` so false success can be measured live.

| Task | Trap | v2 (harder) |
|---|---|---|
| `hidden-items` | missed part: hide items in browse **and** search | search goes through a separate index that never says "unlisted" |
| `bot-labels` | broke behaviour: add `bot/` labels **and keep the old ones** | three modules check labels in three different ways |
| `runner-stats` | wrong assumption: the new record format changes field order | the order is only documented in the runner's changelog; a second module indexes records itself |

Validity checks for every task: the reference solution scores 1, doing nothing scores 0, and the tempting wrong fix scores 0.

Results (free `nvidia/nemotron-3.5-super-vl:free` via OpenRouter, 3 tries per cell):

| Agent | v1: hidden-items | v1: bot-labels | v1: runner-stats | v2 pilot (1 try each) |
|---|---|---|---|---|
| goose | 3/3 | 3/3 | 3/3 | 3/3 |
| pi | 3/3 | 3/3 | 3/3 | — |
| Prime Agent | 3/3 | 3/3 | 3/3 | — |
| mini-SWE-agent | 3/3 | 3/3 | 3/3 | 3/3 |
| OpenCode | 3/3 | 3/3 | 3/3 | — |

**All 45 v1 runs and all 6 v2 pilot runs passed, and every self-reported confidence (95–100%) matched the outcome.** These tasks therefore do not separate agents (a ceiling effect). What they do show: when a task is small or clearly specified, these agents avoid the traps that appear in Half 1, which points at scale and underspecified tasks as the main causes of the real failures.

Note: Half 2 uses a different model (Nemotron) from Half 1 (Qwen3.8), so compare patterns, not exact numbers.

## Limits
- One model per half, one sample of 60 tasks, synthetic Harbor tasks.
- The failure notes are AI drafts; the rubric labels come from one Claude pass plus an independent AI grader, and 15 notes were cross-checked by Claude (not by a human).
- "Hidden-test mismatch" is a judgement that the issue text does not state what the tests require; some of those tasks may still be solvable by inference.

## Run it
```bash
uv sync
uv run python scripts/build_index.py && uv run --with pandas python scripts/pick_sample.py
uv run python scripts/locate.py && uv run python scripts/offsets.py && uv run python scripts/fetch_rows.py
uv run python scripts/make_viewer.py            # open data/viewer/index.html
OPENROUTER_API_KEY=... PYTHONPATH=scripts uv run python scripts/judge_claims.py
uv run python scripts/report.py

# Half 2 (needs Harbor): oracle/nop checks, then agents
./run_agents.sh goose
TASKS="hidden-items-v2 bot-labels-v2 runner-stats-v2" ./run_agents.sh goose
```

## Credits
Data: Ahmad, Ludwig, Majumdar, Ginsburg. *Open-SWE-Traces: Advancing Dual-Mode Multilingual Distillation for Software Engineering Agents.* Findings of EMNLP 2026. CC BY 4.0.

## License
Apache-2.0
