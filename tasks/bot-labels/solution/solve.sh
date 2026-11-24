#!/bin/bash
# Reference: ADD the new labels next to the old ones; only add_approval switches to the prefix.
python3 - <<'PY'
p = "/app/mergebot.py"
s = open(p).read()
s = s.replace('MERGE_LABELS = ["approved", "automerge", "lgtm"]',
              'MERGE_LABELS = ["bot/approved", "approved", "bot/automerge", "automerge", "lgtm"]')
s = s.replace('HOLD_LABELS = ["hold", "blocked"]', 'HOLD_LABELS = ["bot/hold", "hold", "blocked"]')
s = s.replace('if "approved" not in mr["labels"]:\n        mr["labels"].append("approved")',
              'if "bot/approved" not in mr["labels"]:\n        mr["labels"].append("bot/approved")')
open(p, "w").write(s)
PY
echo '{"fixed": true, "confidence": 95}' > /app/report.json
