"""Fetch the full sampled runs one row at a time from the Hugging Face dataset viewer API.

Uses the positions from offsets.py, checks every row is the expected trajectory and not truncated,
and saves one JSON object per line to data/runs.jsonl. Already-fetched runs are skipped on rerun.
"""

import json
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import duckdb

URL = "https://datasets-server.huggingface.co/rows?dataset=nvidia/Open-SWE-Traces&config=v2.0&split={agent}&offset={offset}&length=1"
OUT = Path("data/runs.jsonl")

todo = duckdb.sql("""
    SELECT o.agent, o.trajectory_id, o.offset, s.stratum
    FROM 'data/offsets.parquet' o JOIN 'data/sample_index.parquet' s USING (agent, trajectory_id)
""").fetchall()
done = set()
if OUT.exists():
    done = {json.loads(line)["trajectory_id"] for line in OUT.open()}


def fetch(item):
    agent, trajectory_id, offset, stratum = item
    time.sleep(1)  # stay under the API rate limit
    for attempt in range(6):
        try:
            with urllib.request.urlopen(URL.format(agent=agent, offset=offset), timeout=60) as response:
                payload = json.load(response)
            result = payload["rows"][0]
            row = result["row"]
            if row["trajectory_id"] != trajectory_id:
                return f"MISMATCH {agent} {offset}"
            if result.get("truncated_cells"):
                return f"TRUNCATED {agent} {trajectory_id}"
            return {**row, "agent": agent, "stratum": stratum}
        except Exception as error:  # network hiccups, rate limits (HTTP 429)
            last = error
            wait = 30 * (attempt + 1) if "429" in str(error) else 2 ** attempt
            time.sleep(wait)
    return f"FAILED {agent} {trajectory_id}: {last}"


pending = [item for item in todo if item[1] not in done]
print(f"{len(done)} already saved, fetching {len(pending)}", flush=True)
problems = []
with OUT.open("a") as out, ThreadPoolExecutor(max_workers=1) as pool:
    for i, result in enumerate(pool.map(fetch, pending), 1):
        if isinstance(result, str):
            problems.append(result)
        else:
            out.write(json.dumps(result) + "\n")
        if i % 50 == 0:
            print(f"{i}/{len(pending)}", flush=True)
print("problems:", problems or "none")
print("saved runs:", sum(1 for _ in OUT.open()))
