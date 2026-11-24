"""Agreement between grader A (Claude, from notes) and grader B (AI, from raw evidence): Cohen's kappa."""

import json
from collections import Counter

NAMES = {1: "unwired code", 2: "missed part", 3: "wrong location", 4: "broke behaviour",
         5: "wrong assumption", 6: "hidden-test mismatch", 7: "looks correct", 8: "other"}

A = {r["trajectory_id"]: r["type"] for r in json.load(open("results/labels_claude_from_notes.json"))}
B = {json.loads(l)["trajectory_id"]: json.loads(l)["type"] for l in open("results/labels_ai_from_evidence.jsonl")}
both = [t for t in A if t in B]
n = len(both)
agree = sum(A[t] == B[t] for t in both)
pa = Counter(A[t] for t in both); pb = Counter(B[t] for t in both)
expected = sum(pa[k] * pb[k] for k in NAMES) / (n * n)
kappa = (agree / n - expected) / (1 - expected)
print(f"labelled by both: {n} · raw agreement {agree}/{n} ({agree / n:.0%}) · Cohen's kappa {kappa:.2f}")

# A coarser view that matters for the headline: agent mistake (1-5) vs task/grader problem (6-7)
group = lambda k: "agent mistake" if k <= 5 else ("task/grader" if k in (6, 7) else "other")
ga = sum(group(A[t]) == group(B[t]) for t in both)
print(f"agree on 'agent mistake' vs 'task/grader problem': {ga}/{n} ({ga / n:.0%})")

print(f"\n{'type':22} {'grader A':>8} {'grader B':>8}")
for k, name in NAMES.items():
    print(f"{k} {name:20} {pa[k]:>8} {pb[k]:>8}")
