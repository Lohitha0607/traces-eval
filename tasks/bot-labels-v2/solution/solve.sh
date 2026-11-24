#!/bin/bash
# Reference: add the prefixed labels next to the old ones in all three readers; approve with the prefix.
python3 - <<'PY'
def edit(path, old, new):
    s = open(path).read()
    assert old in s, (path, old)
    open(path, "w").write(s.replace(old, new))

edit("/app/mrbot/labels.py", "MERGE_LABELS = [APPROVED, AUTOMERGE, LGTM]\nHOLD_LABELS = [HOLD, BLOCKED]",
     'BOT_APPROVED = "bot/approved"\nBOT_AUTOMERGE = "bot/automerge"\nBOT_HOLD = "bot/hold"\n\n'
     "MERGE_LABELS = [BOT_APPROVED, APPROVED, BOT_AUTOMERGE, AUTOMERGE, LGTM]\nHOLD_LABELS = [BOT_HOLD, HOLD, BLOCKED]")
edit("/app/mrbot/approve.py", "if labels.APPROVED not in mr[\"labels\"]:\n        mr[\"labels\"].append(labels.APPROVED)",
     "if labels.BOT_APPROVED not in mr[\"labels\"]:\n        mr[\"labels\"].append(labels.BOT_APPROVED)")
edit("/app/mrbot/housekeeping.py", 'tag in ("hold",)', 'tag in ("hold", "bot/hold")')
edit("/app/mrbot/notify.py", 't.lower() == "approved"', 't.lower() in ("approved", "bot/approved")')
PY
echo '{"fixed": true, "confidence": 95}' > /app/report.json
