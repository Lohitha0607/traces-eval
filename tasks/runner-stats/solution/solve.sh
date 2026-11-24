#!/bin/bash
# Reference: read the field order from "_format" (new format: tries FIRST), skip metadata keys.
cat > /app/stats.py <<'PY'
"""Summarise test-runner statistics (old format: [failures, tries]; new: see "_format")."""

import json


def _records(stats):
    fields = stats.get("_format", ["failures", "tries"])
    for name, record in stats.items():
        if name.startswith("_"):
            continue
        yield dict(zip(fields, record))


def count_failures(stats):
    return sum(r["failures"] for r in _records(stats))


def summarize(path):
    with open(path) as f:
        stats = json.load(f)
    records = list(_records(stats))
    return {"tests": len(records), "failures": sum(r["failures"] for r in records),
            "tries": sum(r["tries"] for r in records)}
PY
echo '{"fixed": true, "confidence": 95}' > /app/report.json
