"""Build a local HTML viewer for the sampled runs: an index table plus one page per run.

Open data/viewer/index.html in a browser. Each run page shows the task, every message and tool
call in order, the agent's final message, and the agent's patch next to the reference patch.
"""

import html
import json
from pathlib import Path

RUNS = Path("data/runs.jsonl")
OUT = Path("data/viewer")
STYLE = """
body { font-family: -apple-system, sans-serif; margin: 24px; max-width: 1100px; color: #222; }
table { border-collapse: collapse; width: 100%; font-size: 13px; }
td, th { border: 1px solid #ddd; padding: 4px 6px; text-align: left; vertical-align: top; }
tr.fail { background: #fff3f3; } tr.pass { background: #f3fff5; }
.msg { border-left: 4px solid #ccc; margin: 10px 0; padding: 6px 10px; }
.system, .user { border-color: #888; } .assistant { border-color: #2a6; } .tool { border-color: #36c; }
.role { font-weight: bold; font-size: 12px; text-transform: uppercase; color: #555; }
pre { white-space: pre-wrap; word-break: break-word; font-size: 12px; background: #f7f7f7; padding: 6px; }
.final { border: 2px solid #c60; padding: 8px; }
"""


def text_of(content) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    return json.dumps(content, indent=2, ensure_ascii=False)


def final_message(messages) -> str:
    for message in reversed(messages):
        if message.get("role") == "assistant" and text_of(message.get("content")).strip():
            return text_of(message.get("content"))
    return ""


def patch_of(value) -> str:
    if isinstance(value, dict):
        return value.get("patch", "") or ""
    if isinstance(value, str):
        try:
            return json.loads(value).get("patch", "")
        except (ValueError, AttributeError):
            return value
    return ""


def page(title: str, body: str) -> str:
    return f"<!doctype html><meta charset='utf-8'><title>{html.escape(title)}</title><style>{STYLE}</style>{body}"


def run_page(run: dict) -> str:
    md = run.get("metadata") or {}
    messages = run.get("messages") or []
    parts = [
        f"<p><a href='index.html'>← all runs</a></p>",
        f"<h2>{html.escape(run['instance_id'])} · {run['agent']}</h2>",
        f"<p><b>resolved:</b> {run['resolved']} · <b>stratum:</b> {run['stratum']} · "
        f"<b>category:</b> {html.escape(str(md.get('category')))} · <b>messages:</b> {len(messages)}</p>",
        f"<h3>Final message</h3><div class='final'><pre>{html.escape(final_message(messages))}</pre></div>",
        "<h3>Conversation</h3>",
    ]
    for i, message in enumerate(messages):
        role = message.get("role", "?")
        body = text_of(message.get("content"))
        thinking = text_of(message.get("reasoning_content")).strip()
        if thinking:
            body = f"[thinking]\n{thinking}\n\n[says]\n{body}"
        calls = message.get("tool_calls")
        if calls:
            body += "\n\n[tool calls]\n" + text_of(calls)
        parts.append(f"<div class='msg {role}'><div class='role'>#{i} {role}</div><pre>{html.escape(body)}</pre></div>")
    parts.append(f"<h3>Agent patch</h3><pre>{html.escape(patch_of(md.get('model_patch')))}</pre>")
    parts.append(f"<h3>Reference patch</h3><pre>{html.escape(patch_of(md.get('reference_patch')))}</pre>")
    return page(f"{run['agent']} {run['instance_id']}", "\n".join(parts))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    runs = [json.loads(line) for line in RUNS.open()]
    runs.sort(key=lambda r: (r["stratum"], r["instance_id"], r["agent"]))
    rows = []
    for run in runs:
        name = f"{run['agent']}__{run['trajectory_id']}.html"
        (OUT / name).write_text(run_page(run), encoding="utf-8")
        final = final_message(run.get("messages") or [])[:160]
        css = "pass" if run["resolved"] == 1 else "fail"
        rows.append(
            f"<tr class='{css}'><td>{run['stratum']}</td><td>{html.escape(run['instance_id'])}</td>"
            f"<td>{run['agent']}</td><td>{run['resolved']}</td><td>{len(run.get('messages') or [])}</td>"
            f"<td><a href='{name}'>{html.escape(final) or '(no final message)'}</a></td></tr>"
        )
    table = (
        "<h2>traces-eval sample</h2><p>Red = failed, green = solved. Click a final message to open the run.</p>"
        "<table><tr><th>stratum</th><th>task</th><th>agent</th><th>resolved</th><th>msgs</th><th>final message</th></tr>"
        + "\n".join(rows)
        + "</table>"
    )
    (OUT / "index.html").write_text(page("traces-eval sample", table), encoding="utf-8")
    print(f"wrote {len(runs)} run pages → {OUT / 'index.html'}")


if __name__ == "__main__":
    main()
