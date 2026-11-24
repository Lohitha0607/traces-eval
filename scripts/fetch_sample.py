"""Download the full runs (messages, tools, patches) for the sampled trajectories only."""

import duckdb

AGENTS = ["claudecode", "opencode", "openhands", "sweagent", "minisweagent"]
BASE = "hf://datasets/nvidia/Open-SWE-Traces/data/{agent}/qwen38_flash_next/swe-rebench-v2/train-*.parquet"

con = duckdb.connect()
con.execute("CREATE TABLE want AS SELECT trajectory_id, agent, stratum FROM 'data/sample_index.parquet'")
parts = []
for agent in AGENTS:
    con.execute(f"""
        CREATE TABLE runs_{agent} AS
        SELECT '{agent}' AS agent, t.*
        FROM read_parquet('{BASE.format(agent=agent)}') t
        WHERE t.trajectory_id IN (SELECT trajectory_id FROM want WHERE agent = '{agent}')
    """)
    print(agent, con.execute(f"SELECT count(*) FROM runs_{agent}").fetchone()[0], "runs", flush=True)
    parts.append(f"SELECT * FROM runs_{agent}")
con.execute(f"""
    COPY (SELECT r.*, w.stratum FROM ({' UNION ALL '.join(parts)}) r JOIN want w USING (trajectory_id, agent))
    TO 'data/sample.parquet' (FORMAT parquet)
""")
print("saved data/sample.parquet:", con.execute("SELECT count(*) FROM 'data/sample.parquet'").fetchone()[0], "runs")
