"""Pick a fair sample: tasks that all 5 agents attempted, so every agent faces the same tasks.

Stratified by how many agents solved the task: mixed tasks (1-4 agents solved) show why one
agent fails where others succeed; nobody-solved and all-solved tasks are the two baselines.
"""

import duckdb

STRATA = {"mixed": 30, "none": 20, "all": 10}  # 60 tasks x 5 agents = 300 runs
SEED = 0.42  # fixed, so the sample can be rebuilt exactly

con = duckdb.connect()
con.execute("CREATE TABLE idx AS SELECT * FROM 'data/index.parquet'")
shared = con.execute("""
    SELECT instance_id, sum(resolved) AS n_solved
    FROM idx GROUP BY instance_id HAVING count(DISTINCT agent) = 5
""").fetchdf()
print(f"tasks attempted by all 5 agents: {len(shared):,}")
print("how many agents solved each shared task:")
print(shared["n_solved"].value_counts().sort_index().to_string())

con.execute(f"SELECT setseed({SEED})")
con.execute("""
    CREATE TABLE strata AS
    SELECT instance_id,
           CASE WHEN sum(resolved) = 0 THEN 'none' WHEN sum(resolved) = 5 THEN 'all' ELSE 'mixed' END AS stratum
    FROM idx GROUP BY instance_id HAVING count(DISTINCT agent) = 5
""")
con.execute("CREATE TABLE picked (instance_id VARCHAR, stratum VARCHAR)")
for stratum, n in STRATA.items():
    con.execute(f"""
        INSERT INTO picked
        SELECT instance_id, stratum FROM strata WHERE stratum = '{stratum}' ORDER BY random() LIMIT {n}
    """)
con.execute("""
    COPY (SELECT idx.*, picked.stratum FROM idx JOIN picked USING (instance_id) ORDER BY instance_id, agent)
    TO 'data/sample_index.parquet' (FORMAT parquet)
""")
print(con.execute("""
    SELECT agent, count(*) AS runs, sum(CASE WHEN resolved=1 THEN 1 ELSE 0 END) AS solved,
           sum(CASE WHEN resolved=0 THEN 1 ELSE 0 END) AS failed
    FROM 'data/sample_index.parquet' GROUP BY agent ORDER BY agent
""").fetchdf().to_string(index=False))
