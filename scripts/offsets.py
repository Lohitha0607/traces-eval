"""Turn (file, row) into the row's position in the Hugging Face split, so single rows can be fetched.

The split for each agent concatenates two file patterns in order (from the dataset card):
  data/{agent}/qwen38_flash_next/*/*.parquet, then data/{agent}/qwen38_flash_next/*/*/*.parquet
"""

import duckdb

AGENTS = ["claudecode", "opencode", "openhands", "sweagent", "minisweagent"]
PATTERNS = [
    "hf://datasets/nvidia/Open-SWE-Traces/data/{agent}/qwen38_flash_next/*/*.parquet",
    "hf://datasets/nvidia/Open-SWE-Traces/data/{agent}/qwen38_flash_next/*/*/*.parquet",
]

con = duckdb.connect()
rows = []
for agent in AGENTS:
    start = 0
    for pattern in PATTERNS:
        files = sorted(r[0] for r in con.execute(f"SELECT file FROM glob('{pattern.format(agent=agent)}')").fetchall())
        for f in files:
            n = con.execute(f"SELECT num_rows FROM parquet_file_metadata('{f}')").fetchone()[0]
            rows.append((agent, f, start, n))
            start += n
    print(agent, "split rows:", start, flush=True)
con.execute("CREATE TABLE files (agent VARCHAR, filename VARCHAR, start BIGINT, n BIGINT)")
con.executemany("INSERT INTO files VALUES (?, ?, ?, ?)", rows)
con.execute("""
    COPY (SELECT l.agent, l.trajectory_id, f.start + l.file_row_number AS offset
          FROM 'data/locations.parquet' l JOIN files f USING (agent, filename))
    TO 'data/offsets.parquet' (FORMAT parquet)
""")
print(con.execute("SELECT * FROM 'data/offsets.parquet' LIMIT 3").fetchall())
