"""Write results/fairness_summary.md, results/fairness_by_size.png and results/fair_tasks.csv."""

import duckdb
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

con = duckdb.connect()
con.execute("""
CREATE TABLE runs AS
WITH sizes AS (
  SELECT instance_id, len(list_filter(string_split(patch, chr(10)),
         lambda x: starts_with(x, '+') AND NOT starts_with(x, '+++'))) AS added_lines
  FROM 'data/scaleswe.parquet')
SELECT i.agent, i.instance_id, i.resolved, f.unfair, s.added_lines,
       CASE WHEN added_lines <= 10 THEN '≤10' WHEN added_lines <= 30 THEN '11–30'
            WHEN added_lines <= 100 THEN '31–100' ELSE '>100' END AS fix_size
FROM 'data/index.parquet' i JOIN 'results/fairness_scaleswe.parquet' f USING (instance_id) JOIN sizes s USING (instance_id)
""")
n_tasks, n_flagged = con.execute("SELECT count(*), sum(unfair::INT) FROM 'results/fairness_scaleswe.parquet'").fetchone()
overall = con.execute("SELECT unfair, count(DISTINCT instance_id), count(*), avg(resolved) FROM runs GROUP BY unfair ORDER BY unfair").fetchall()
per_agent = con.execute("""SELECT agent, avg(resolved) FILTER (WHERE NOT unfair), avg(resolved) FILTER (WHERE unfair)
                           FROM runs GROUP BY agent ORDER BY agent""").fetchall()
order = ["≤10", "11–30", "31–100", ">100"]
by_size = {r[0]: r[1:] for r in con.execute("""SELECT fix_size, avg(resolved) FILTER (WHERE NOT unfair), avg(resolved) FILTER (WHERE unfair),
                                                count(*) FILTER (WHERE NOT unfair), count(*) FILTER (WHERE unfair) FROM runs GROUP BY fix_size""").fetchall()}

lines = ["# Fairness check: tests that need what the issue never says", "",
         f"Checked **{n_tasks:,}** Scale-SWE tasks (the tasks behind Open-SWE-Traces). A task is flagged when its hidden test",
         "uses a name (function, method, class, constant) or a literal that the correct fix newly introduces and the issue never mentions.",
         f"**Flagged: {n_flagged:,} ({n_flagged / n_tasks:.1%}).** The rule uses no AI (`fairness/check.py`).", "",
         "## Flagged tasks are solved about half as often", "",
         "Open-SWE-Traces runs (scale-swe, xhigh, 5 agents, same model):", "",
         "| | Tasks | Runs | Solve rate |", "|---|---|---|---|"]
for unfair, tasks, runs, rate in overall:
    lines.append(f"| {'flagged' if unfair else 'not flagged'} | {tasks:,} | {runs:,} | **{rate:.1%}** |")
lines += ["", "| Agent | Not flagged | Flagged |", "|---|---|---|"]
lines += [f"| {a} | {fair:.1%} | {flag:.1%} |" for a, fair, flag in per_agent]
lines += ["", "Same size of correct fix (added non-test lines):", "", "| Fix size | Not flagged | Flagged |", "|---|---|---|"]
lines += [f"| {s} lines | {by_size[s][0]:.1%} (n={by_size[s][2]:,}) | {by_size[s][1]:.1%} (n={by_size[s][3]:,}) |" for s in order]
lines += ["", "## Validation and limits",
          "- On the 60 hand-analysed tasks the rule agrees with the Half 1 rubric only weakly (53%; precision 46%, recall 32%), so it is a coarse screen, not a verdict per task.",
          "- It never flagged the 10 tasks that all five agents solved.",
          "- The solve-rate gap is a correlation; the Harbor experiment (`tasks/proof-*`) tests the cause on a flagged task.",
          "- Scale-SWE has two graders: a generated `f2p_script` and the real PR tests (`FAIL_TO_PASS`). They can disagree (e.g. clusterscope: the generated test accepts the agents' solution, the PR tests do not)."]
open("results/fairness_summary.md", "w").write("\n".join(lines) + "\n")

fig, ax = plt.subplots(figsize=(7, 4))
xs = range(len(order))
ax.bar([x - 0.2 for x in xs], [by_size[s][0] for s in order], 0.4, label="not flagged", color="#4f81bd")
ax.bar([x + 0.2 for x in xs], [by_size[s][1] for s in order], 0.4, label="flagged (test needs info not in the issue)", color="#c0504d")
ax.set_xticks(list(xs)); ax.set_xticklabels([f"{s} lines" for s in order]); ax.set_ylim(0, 1)
ax.set_ylabel("solve rate"); ax.set_xlabel("size of the correct fix"); ax.legend(fontsize=8)
ax.set_title("Agents solve flagged tasks about half as often, at every fix size")
plt.tight_layout(); plt.savefig("results/fairness_by_size.png", dpi=150)

con.execute("""COPY (SELECT instance_id, repo, unfair AS flagged, missing_names, missing_literals
                     FROM 'results/fairness_scaleswe.parquet' ORDER BY instance_id) TO 'results/fair_tasks.csv' (HEADER)""")
print(open("results/fairness_summary.md").read())
