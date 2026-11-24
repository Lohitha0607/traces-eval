"""Build a small index of every run (no message text) for the 5 agents.

Reads only the light columns of nvidia/Open-SWE-Traces v2.0, source scale-swe,
reasoning effort xhigh (the top-level train-*.parquet files), straight from Hugging Face.
"""

import duckdb

AGENTS = ["claudecode", "opencode", "openhands", "sweagent", "minisweagent"]
BASE = "hf://datasets/nvidia/Open-SWE-Traces/data/{agent}/qwen38_flash_next/scale-swe/train-*.parquet"

con = duckdb.connect()
parts = [
    f"""SELECT '{agent}' AS agent, instance_id, trajectory_id, repo, language, resolved,
               metadata.category AS category
        FROM read_parquet('{BASE.format(agent=agent)}')"""
    for agent in AGENTS
]
con.execute(f"COPY ({' UNION ALL '.join(parts)}) TO 'data/index.parquet' (FORMAT parquet)")
print(con.execute("""
    SELECT agent, count(*) AS runs, count(DISTINCT instance_id) AS tasks,
           round(avg(CASE WHEN resolved = 1 THEN 1.0 ELSE 0 END) * 100, 1) AS solved_pct,
           sum(CASE WHEN resolved = -1 THEN 1 ELSE 0 END) AS unknown
    FROM 'data/index.parquet' GROUP BY agent ORDER BY agent
""").fetchdf().to_string(index=False))
