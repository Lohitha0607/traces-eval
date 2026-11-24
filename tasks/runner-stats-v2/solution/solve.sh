#!/bin/bash
# Reference: one normaliser that knows both versions (2.0: [tries, failures, skips] under "tests"),
# used by the summary AND by flaky_tests.
cat > /app/ci_report/load.py <<'PY'
import json


def load_stats(path):
    with open(path) as f:
        return json.load(f)


def normalized(stats):
    """{name: (failures, tries)} for runner 1.x and 2.0 files."""
    if stats.get("runner_version") == 2:
        return {name: (rec[1], rec[0]) for name, rec in stats["tests"].items()}
    return {name: (rec[0], rec[1]) for name, rec in stats.items()}


def records(stats):
    for name, (failures, tries) in normalized(stats).items():
        yield name, failures, tries
PY
cat > /app/ci_report/flaky.py <<'PY'
from ci_report.load import normalized


def flaky_tests(stats):
    return sorted(name for name, (failures, tries) in normalized(stats).items() if 0 < failures < tries)
PY
echo '{"fixed": true, "confidence": 95}' > /app/report.json
