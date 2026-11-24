#!/bin/bash
# Half 2: run agents on the traces-eval Harbor tasks, 3 tries each, one trial at a time.
# Usage: ./run_agents.sh <agent> [model]   e.g. ./run_agents.sh goose
# Needs OPENROUTER_API_KEY. Uses Harbor from ~/Desktop/harbor (the branch with the prime-agent adapter).
set -uo pipefail
cd "$(dirname "$0")"
AGENT="${1:?usage: ./run_agents.sh <agent> [model]}"
MODEL="${2:-openrouter/nvidia/nemotron-3.5-super-vl:free}"
TRIES="${TRIES:-3}"
for task in hidden-items bot-labels runner-stats; do
  job="run-$AGENT-$task"
  if [ -f "jobs/$job/result.json" ]; then echo "skip $job (done)"; continue; fi
  rm -rf "jobs/$job"
  echo "$(date +%H:%M:%S) start $job"
  (cd ~/Desktop/harbor && NO_COLOR=1 uv run harbor run -p "$OLDPWD/tasks/$task" -a "$AGENT" -m "$MODEL" \
     -k "$TRIES" -n 1 -o "$OLDPWD/jobs" --job-name "$job") > "jobs/$job.log" 2>&1
  echo "$(date +%H:%M:%S) done  $job (exit $?)"
done
echo "ALL DONE ($AGENT)"
