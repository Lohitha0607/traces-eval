"""Fairness check: does the hidden test need something the issue never mentions?

For each Scale-SWE task we look at three texts:
  - the issue (problem_statement), which is all the agent is told,
  - the correct fix (patch),
  - the hidden test (f2p_script, or f2p_patch).

A task is flagged when the test uses a NAME (function, method, class, constant) or a LITERAL
(string or number) that the correct fix newly introduces, and that does not appear in the issue.
An agent could not reasonably guess such a detail, so failing on it is not the agent's fault.
This is a plain rule (no AI), so it gives the same answer every time and scales to every task.
"""

import json
import re
import sys

import duckdb

DEF_RE = re.compile(r"^\+\s*(?:async\s+)?(?:def|class)\s+([A-Za-z_]\w*)")
ASSIGN_RE = re.compile(r"^\+(?:self\.|    self\.|        self\.)?([A-Za-z_]\w*)\s*(?::[^=]+)?=[^=]")
TOPLEVEL_ASSIGN_RE = re.compile(r"^\+([A-Za-z_]\w*)\s*(?::[^=]+)?=[^=]")
SELF_ATTR_RE = re.compile(r"^\+\s*self\.([A-Za-z_]\w*)\s*(?::[^=]+)?=[^=]")
NAME_RE = re.compile(r"[A-Za-z_]\w*")
STRING_RE = re.compile(r"""(?:"([^"\\\n]{4,80})"|'([^'\\\n]{4,80})')""")
NUMBER_RE = re.compile(r"(?<![\w.])(\d+\.\d+|\d{3,})(?![\w.])")
COMMON = {"self", "cls", "args", "kwargs", "result", "value", "data", "name", "test", "main", "None",
          "True", "False", "return", "assert", "import", "from", "class", "def", "init", "__init__"}


TEST_PATH_RE = re.compile(r"(^|/)(tests?|testing)(/|$)|(^|/)test_[^/]*$|_test\.py$|conftest\.py$")


def patch_lines(patch: str):
    """Added lines and old/context lines of the fix, skipping test files (they are part of the grader)."""
    added, removed_or_context = [], []
    in_test_file = False
    for line in (patch or "").splitlines():
        if line.startswith("diff --git"):
            path = line.split(" b/")[-1]
            in_test_file = bool(TEST_PATH_RE.search(path))
            continue
        if in_test_file or line.startswith(("+++", "---", "index ", "@@")):
            continue
        (added if line.startswith("+") else removed_or_context).append(line)
    return added, "\n".join(removed_or_context)


def new_names(patch: str) -> set:
    """Names the correct fix defines on added lines and that did not exist in the old code shown."""
    added, old = patch_lines(patch)
    names = set()
    for line in added:
        for rx in (DEF_RE, TOPLEVEL_ASSIGN_RE, SELF_ATTR_RE):
            m = rx.match(line)
            if m:
                names.add(m.group(1))
    old_words = set(NAME_RE.findall(old))
    return {n for n in names if n not in old_words and n not in COMMON and len(n) > 2}


def new_literals(patch: str) -> set:
    """Strings and numbers that appear only on the fix's added lines."""
    added, old = patch_lines(patch)
    added_text = "\n".join(added)
    found = {a or b for a, b in STRING_RE.findall(added_text)} | set(NUMBER_RE.findall(added_text))
    return {x for x in found if x not in old}


def mentioned(token: str, issue: str) -> bool:
    if token in issue:
        return True
    # tolerate formatting differences: case, underscores vs spaces
    loose = token.lower().replace("_", " ")
    return loose in issue.lower().replace("_", " ")


def check(issue: str, patch: str, test: str) -> dict:
    issue = issue or ""
    test = test or ""
    test_words = set(NAME_RE.findall(test))
    defined_in_test = set(re.findall(r"(?:def|class)\s+([A-Za-z_]\w*)", test)) | set(re.findall(r"^\s*([A-Za-z_]\w*)\s*=", test, re.M))
    test_words -= defined_in_test
    needed_names = sorted(n for n in new_names(patch) if n in test_words and not mentioned(n, issue))
    needed_literals = sorted(x for x in new_literals(patch) if x in test and not mentioned(x, issue))
    return {"unfair": bool(needed_names or needed_literals),
            "missing_names": needed_names, "missing_literals": needed_literals}


def main(out_path: str = "results/fairness_scaleswe.parquet") -> None:
    con = duckdb.connect()
    rows = con.execute("""
        SELECT instance_id, repo, problem_statement, patch,
               CASE WHEN coalesce(f2p_script, '') <> '' THEN f2p_script ELSE f2p_patch END AS test
        FROM 'data/scaleswe.parquet'
    """).fetchall()
    results = []
    for instance_id, repo, issue, patch, test in rows:
        r = check(issue, patch, test)
        results.append((instance_id, repo, r["unfair"], json.dumps(r["missing_names"]), json.dumps(r["missing_literals"])))
    con.execute("CREATE TABLE f (instance_id VARCHAR, repo VARCHAR, unfair BOOLEAN, missing_names VARCHAR, missing_literals VARCHAR)")
    con.executemany("INSERT INTO f VALUES (?, ?, ?, ?, ?)", results)
    con.execute(f"COPY f TO '{out_path}' (FORMAT parquet)")
    n, k = con.execute("SELECT count(*), sum(unfair::INT) FROM f").fetchone()
    print(f"checked {n:,} tasks · flagged unfair: {k:,} ({k / n:.1%})")


if __name__ == "__main__":
    main(*sys.argv[1:])
