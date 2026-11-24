"""Step 9: counts, confidence intervals and charts → results/summary.md + results/*.png."""

import json
import math
from collections import Counter, defaultdict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

NAMES = {1: "unwired code", 2: "missed part of request", 3: "wrong location", 4: "broke existing behaviour",
         5: "wrong assumption", 6: "hidden-test mismatch", 7: "looks correct", 8: "other / unclear"}
AGENT_NAMES = {"claudecode": "Claude Code", "opencode": "OpenCode", "openhands": "OpenHands",
               "sweagent": "SWE-agent", "minisweagent": "mini-SWE-agent"}


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (c - h, c + h)


labels = json.load(open("results/labels_claude_from_notes.json"))
claims = {json.loads(l)["trajectory_id"]: json.loads(l) for l in open("results/claims.jsonl")}
runs = {}
for line in open("data/runs.jsonl"):
    r = json.loads(line)
    runs[r["trajectory_id"]] = {"agent": r["agent"], "resolved": r["resolved"], "steps": len(r["messages"]),
                                "category": (r.get("metadata") or {}).get("category")}
agents = list(AGENT_NAMES)
lines = ["# traces-eval results", "",
         "Sample: nvidia/Open-SWE-Traces v2.0, source scale-swe, reasoning xhigh, model Qwen3.8-Flash-Next.",
         "60 tasks attempted by all 5 agents (30 mixed, 20 nobody solved, 10 everybody solved) → 300 runs, 163 failures.", ""]

# 1. False success
lines += ["## 1. Do agents know they failed? (step 6, AI judge on the final message)", "",
          "| Agent | Failed runs | Claimed success | 95% CI | Claimed they verified it |", "|---|---|---|---|---|"]
fs = {}
for a in agents:
    failed = [c for c in claims.values() if c["agent"] == a and c["resolved"] == 0]
    k = sum(c["label"] == "claims_success" for c in failed)
    v = sum(c["label"] == "claims_success" and c["says_verified"] for c in failed)
    lo, hi = wilson(k, len(failed))
    fs[a] = (k, len(failed), lo, hi)
    lines.append(f"| {AGENT_NAMES[a]} | {len(failed)} | {k} ({k / len(failed):.0%}) | {lo:.0%}–{hi:.0%} | {v} ({v / len(failed):.0%}) |")
all_failed = [c for c in claims.values() if c["resolved"] == 0]
k = sum(c["label"] == "claims_success" for c in all_failed)
solved = [c for c in claims.values() if c["resolved"] == 1]
ks = sum(c["label"] == "claims_success" for c in solved)
lo, hi = wilson(k, len(all_failed))
lines += [f"| **All** | {len(all_failed)} | **{k} ({k / len(all_failed):.0%})** | {lo:.0%}–{hi:.0%} | |", "",
          f"Solved runs claimed success {ks}/{len(solved)} ({ks / len(solved):.0%}) of the time, so a success claim barely separates solved from failed runs.", ""]

# 2. Failure types
by_agent = defaultdict(Counter)
for row in labels:
    by_agent[row["agent"]][row["type"]] += 1
total = Counter(row["type"] for row in labels)
n = len(labels)
lines += ["## 2. Why do they fail? (step 8, rubric v1, grader A on all 163 failures)", "",
          "| Type | All agents | 95% CI | " + " | ".join(AGENT_NAMES[a] for a in agents) + " |",
          "|---|---|---|" + "---|" * len(agents)]
for t, name in NAMES.items():
    lo, hi = wilson(total[t], n)
    cells = " | ".join(f"{by_agent[a][t]}" for a in agents)
    lines.append(f"| {t}. {name} | {total[t]} ({total[t] / n:.0%}) | {lo:.0%}–{hi:.0%} | {cells} |")
agent_mistake = sum(total[t] for t in (1, 2, 3, 4, 5))
task_problem = total[6] + total[7]
lines += ["", f"- Agent mistakes (types 1–5): **{agent_mistake} ({agent_mistake / n:.0%})**",
          f"- Task or grader problems (types 6–7): **{task_problem} ({task_problem / n:.0%})**", ""]

# 3. Effort: steps per run
lines += ["## 3. Effort: messages per run", "", "| Agent | Solved (median) | Failed (median) |", "|---|---|---|"]
def median(xs):
    xs = sorted(xs); return xs[len(xs) // 2] if xs else 0
for a in agents:
    s = [r["steps"] for r in runs.values() if r["agent"] == a and r["resolved"] == 1]
    f = [r["steps"] for r in runs.values() if r["agent"] == a and r["resolved"] == 0]
    lines.append(f"| {AGENT_NAMES[a]} | {median(s)} | {median(f)} |")
open("results/summary.md", "w").write("\n".join(lines) + "\n")

# Charts
fig, ax = plt.subplots(figsize=(8, 4))
names = [AGENT_NAMES[a] for a in agents]
rates = [fs[a][0] / fs[a][1] for a in agents]
errs = [[r - fs[a][2] for r, a in zip(rates, agents)], [fs[a][3] - r for r, a in zip(rates, agents)]]
ax.bar(names, rates, yerr=errs, capsize=4, color="#c0504d")
ax.set_ylim(0, 1); ax.set_ylabel("share of FAILED runs")
ax.set_title("Failed runs where the agent still claimed success (95% CI)")
plt.tight_layout(); plt.savefig("results/false_success.png", dpi=150)

fig, ax = plt.subplots(figsize=(9, 4.5))
bottom = [0] * len(agents)
colors = ["#4f81bd", "#9bbb59", "#f79646", "#c0504d", "#8064a2", "#7f7f7f", "#4bacc6", "#d9d9d9"]
for (t, name), color in zip(NAMES.items(), colors):
    vals = [by_agent[a][t] / sum(by_agent[a].values()) for a in agents]
    ax.bar(names, vals, bottom=bottom, label=name, color=color)
    bottom = [b + v for b, v in zip(bottom, vals)]
ax.set_ylabel("share of failures"); ax.set_title("Why each agent failed (rubric v1)")
ax.legend(fontsize=8, bbox_to_anchor=(1.02, 1), loc="upper left")
plt.tight_layout(); plt.savefig("results/failure_types.png", dpi=150)
print(open("results/summary.md").read())
