# Fairness check: tests that need what the issue never says

Checked **20,181** Scale-SWE tasks (the tasks behind Open-SWE-Traces). A task is flagged when its hidden test
uses a name (function, method, class, constant) or a literal that the correct fix newly introduces and the issue never mentions.
**Flagged: 4,874 (24.2%).** The rule uses no AI (`fairness/check.py`).

## Flagged tasks are solved about half as often

Open-SWE-Traces runs (scale-swe, xhigh, 5 agents, same model):

| | Tasks | Runs | Solve rate |
|---|---|---|---|
| not flagged | 13,145 | 59,250 | **68.0%** |
| flagged | 4,034 | 17,230 | **35.5%** |

| Agent | Not flagged | Flagged |
|---|---|---|
| claudecode | 68.4% | 36.1% |
| minisweagent | 67.8% | 36.1% |
| opencode | 66.6% | 33.5% |
| openhands | 69.6% | 36.9% |
| sweagent | 68.1% | 35.1% |

Same size of correct fix (added non-test lines):

| Fix size | Not flagged | Flagged |
|---|---|---|
| ≤10 lines | 78.7% (n=9,359) | 44.0% (n=899) |
| 11–30 lines | 77.1% (n=17,491) | 42.9% (n=2,574) |
| 31–100 lines | 68.2% (n=19,846) | 39.7% (n=5,474) |
| >100 lines | 47.2% (n=12,554) | 29.5% (n=8,283) |

## Validation and limits
- On the 60 hand-analysed tasks the rule agrees with the Half 1 rubric only weakly (53%; precision 46%, recall 32%), so it is a coarse screen, not a verdict per task.
- It never flagged the 10 tasks that all five agents solved.
- The solve-rate gap is a correlation; the Harbor experiment (`tasks/proof-*`) tests the cause on a flagged task.
- Scale-SWE has two graders: a generated `f2p_script` and the real PR tests (`FAIL_TO_PASS`). They can disagree (e.g. clusterscope: the generated test accepts the agents' solution, the PR tests do not).
