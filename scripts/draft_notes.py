"""Step 7 (draft): an AI writes a short failure note for each FAILED run, for a human to check.

It sees a condensed trace (issue, the agent's actions with short outputs, final message) plus the
agent's patch and the reference patch, and the fact that hidden tests say the run FAILED.
"""

import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from claims_rules import final_message
from llm import ask, parse_json

OUT = Path("data/notes_draft.jsonl")
PROMPT = """You are analysing why a coding agent FAILED a GitHub issue. Hidden tests confirm the final patch does NOT resolve the issue.

Compare what the agent did with the reference (correct) patch. Write a precise, factual diagnosis.

Reply with JSON only:
{{
  "note": "<one or two sentences: what went wrong, concretely>",
  "failure_type": "<short label in your own words, e.g. 'wrong location', 'incomplete fix', 'misread requirement', 'broke other behaviour', 'no fix applied'>",
  "ran_tests": "<yes / no / only its own script>",
  "first_wrong_step": <step number where it first went wrong, or null>,
  "confidence": "<high / medium / low>"
}}

ISSUE (truncated):
<<<
{issue}
>>>

AGENT ACTIONS (condensed; [n] = step number):
<<<
{actions}
>>>

AGENT FINAL MESSAGE (truncated):
<<<
{final}
>>>

AGENT PATCH (truncated):
<<<
{patch}
>>>

REFERENCE PATCH (truncated):
<<<
{reference}
>>>"""


def patch_of(value) -> str:
    if isinstance(value, dict):
        return value.get("patch", "") or ""
    try:
        return json.loads(value).get("patch", "")
    except (ValueError, AttributeError, TypeError):
        return value or ""


def condensed(messages, max_chars=14000) -> tuple[str, str]:
    issue = next((m["content"] for m in messages if m.get("role") == "user" and isinstance(m.get("content"), str)), "")
    lines = []
    for i, m in enumerate(messages):
        role = m.get("role")
        if role == "assistant":
            for call in m.get("tool_calls") or []:
                fn = (call.get("function") or {}) if isinstance(call, dict) else {}
                lines.append(f"[{i}] CALL {fn.get('name', '?')}: {str(fn.get('arguments', ''))[:300]}")
            text = m.get("content")
            if isinstance(text, str) and text.strip() and not m.get("tool_calls"):
                lines.append(f"[{i}] SAYS: {text[:200]}")
        elif role == "tool":
            out = m.get("content") if isinstance(m.get("content"), str) else json.dumps(m.get("content"))
            lines.append(f"[{i}] OUTPUT: {out[:250]}")
    text = "\n".join(lines)
    if len(text) > max_chars:  # keep the start and the end, where most decisions happen
        text = text[: max_chars // 2] + "\n...[middle steps cut]...\n" + text[-max_chars // 2:]
    return issue[:3000], text


runs = [json.loads(line) for line in open("data/runs.jsonl") if json.loads(line)["resolved"] == 0]
limit = int(sys.argv[1]) if len(sys.argv) > 1 else len(runs)
done = {json.loads(l)["trajectory_id"] for l in OUT.open()} if OUT.exists() else set()
todo = [r for r in runs[:limit] if r["trajectory_id"] not in done]


def draft(run):
    md = run.get("metadata") or {}
    issue, actions = condensed(run["messages"])
    reply, usage = ask(PROMPT.format(
        issue=issue, actions=actions, final=final_message(run["messages"])[-1500:],
        patch=patch_of(md.get("model_patch"))[:3000], reference=patch_of(md.get("reference_patch"))[:3000],
    ), max_tokens=5000)
    result = parse_json(reply)
    return {"trajectory_id": run["trajectory_id"], "agent": run["agent"], "instance_id": run["instance_id"],
            "stratum": run["stratum"], **{k: result.get(k) for k in ("note", "failure_type", "ran_tests", "first_wrong_step", "confidence")},
            "usage": usage}


with OUT.open("a") as out, ThreadPoolExecutor(max_workers=4) as pool:
    for row in pool.map(draft, todo):
        out.write(json.dumps(row) + "\n")
        out.flush()
print(f"drafted {len(todo)} (total {len(done) + len(todo)})")
