"""Find where each sampled run sits (file + row), reading only the small trajectory_id column."""

import duckdb

AGENTS = ["claudecode", "opencode", "openhands", "sweagent", "minisweagent"]
BASE = "hf://datasets/nvidia/Open-SWE-Traces/data/{agent}/qwen38_flash_next/scale-swe/train-*.parquet"

con = duckdb.connect()
con.execute("CREATE TABLE want AS SELECT trajectory_id, agent FROM 'data/sample_index.parquet'")
parts = [
    f"""SELECT '{agent}' AS agent, trajectory_id, filename, file_row_number
        FROM read_parquet('{BASE.format(agent=agent)}', filename = true, file_row_number = true)"""
    for agent in AGENTS
]
con.execute(f"""
    COPY (SELECT l.* FROM ({' UNION ALL '.join(parts)}) l JOIN want USING (agent, trajectory_id))
    TO 'data/locations.parquet' (FORMAT parquet)
""")
print(con.execute("SELECT agent, count(*) FROM 'data/locations.parquet' GROUP BY agent ORDER BY agent").fetchall())
