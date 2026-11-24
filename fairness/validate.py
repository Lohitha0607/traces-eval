"""Compare the fairness checker with the Half 1 rubric labels on our 60 sampled tasks.

Task-level label from Half 1: 'unfair' if most of the task's failed runs were labelled
hidden-test mismatch (type 6) by grader A; 'agent mistake' if most were types 1-5.
Tasks that every agent solved are reported separately (no failure labels).
"""

import json
from collections import Counter, defaultdict

import duckdb

con = duckdb.connect()
flags = dict(con.execute("SELECT instance_id, unfair FROM 'results/fairness_scaleswe.parquet'").fetchall())
labels = json.load(open("results/labels_claude_from_notes.json"))
strata = dict(con.execute("SELECT DISTINCT instance_id, stratum FROM 'data/sample_index.parquet'").fetchall())

by_task = defaultdict(list)
for row in labels:
    by_task[row["instance_id"]].append(row["type"])

table = Counter()
rows = []
for task, types in by_task.items():
    c = Counter("unfair" if t == 6 else ("agent" if t <= 5 else "other") for t in types)
    human = c.most_common(1)[0][0]
    if human == "other":
        continue
    checker = "unfair" if flags.get(task) else "fair"
    table[(human, checker)] += 1
    rows.append((task, human, checker, dict(c)))

tp, fn = table[("unfair", "unfair")], table[("unfair", "fair")]
fp, tn = table[("agent", "unfair")], table[("agent", "fair")]
print("tasks with failures, Half 1 label vs checker:")
print(f"  Half 1 'unfair'        → checker unfair {tp:2} · fair {fn:2}")
print(f"  Half 1 'agent mistake' → checker unfair {fp:2} · fair {tn:2}")
print(f"  agreement {(tp + tn) / (tp + tn + fp + fn):.0%} · precision {tp / max(tp + fp, 1):.0%} · recall {tp / max(tp + fn, 1):.0%}")
solved_all = [t for t, s in strata.items() if s == "all"]
print(f"tasks every agent solved: {len(solved_all)}, flagged unfair by the checker: {sum(bool(flags.get(t)) for t in solved_all)}")
json.dump(rows, open("results/fairness_validation.json", "w"), indent=1)
