"""Step 8b: an independent AI grader applies rubric.md to the raw evidence (not the step-7 notes)."""

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from claims_rules import final_message
from draft_notes import condensed, patch_of
from llm import ask, parse_json

OUT = Path("results/labels_ai_from_evidence.jsonl")
RUBRIC = Path("rubric.md").read_text()
PROMPT = """You classify why a coding agent FAILED a GitHub issue (hidden tests confirm the patch does not resolve it).
Use this rubric and pick exactly ONE primary type number.

{rubric}

Important: decide type 6 only if the hidden tests clearly need something the ISSUE TEXT does not state
(compare the issue with the reference patch). Decide type 7 only if the agent's patch does what the issue asks.

Reply with JSON only: {{"type": <1-8>, "over_engineered": true/false, "why": "<one sentence>"}}

ISSUE:
<<<
{issue}
>>>

AGENT ACTIONS (condensed):
<<<
{actions}
>>>

AGENT FINAL MESSAGE:
<<<
{final}
>>>

AGENT PATCH:
<<<
{patch}
>>>

REFERENCE PATCH:
<<<
{reference}
>>>"""

runs = {json.loads(l)["trajectory_id"]: json.loads(l) for l in open("data/runs.jsonl")}
targets = [json.loads(l)["trajectory_id"] for l in open("results/notes_draft.jsonl")]
done = {json.loads(l)["trajectory_id"] for l in OUT.open()} if OUT.exists() else set()


def grade(trajectory_id):
    run = runs[trajectory_id]
    md = run.get("metadata") or {}
    issue, actions = condensed(run["messages"], max_chars=8000)
    reply, usage = ask(PROMPT.format(
        rubric=RUBRIC, issue=issue, actions=actions, final=final_message(run["messages"])[-1000:],
        patch=patch_of(md.get("model_patch"))[:3000], reference=patch_of(md.get("reference_patch"))[:3000],
    ), max_tokens=3000)
    result = parse_json(reply)
    return {"trajectory_id": trajectory_id, "agent": run["agent"], "type": result.get("type"),
            "over_engineered": result.get("over_engineered"), "why": result.get("why"), "usage": usage}


if __name__ == "__main__":
    todo = [t for t in targets if t not in done]
    with OUT.open("a") as out, ThreadPoolExecutor(max_workers=4) as pool:
        for row in pool.map(grade, todo):
            out.write(json.dumps(row) + "\n")
            out.flush()
    print(f"graded {len(todo)}")
