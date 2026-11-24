#!/bin/bash
# Hidden grader: reward 1 only if every hidden test passes. Also keeps the agent's self-report.
mkdir -p /logs/verifier
cp /app/report.json /logs/verifier/report.json 2>/dev/null || echo '{"missing": true}' > /logs/verifier/report.json
cd /app && python -m pytest -q /tests/test_hidden.py > /logs/verifier/pytest.txt 2>&1
if [ $? -eq 0 ]; then echo 1 > /logs/verifier/reward.txt; else echo 0 > /logs/verifier/reward.txt; fi
tail -5 /logs/verifier/pytest.txt
