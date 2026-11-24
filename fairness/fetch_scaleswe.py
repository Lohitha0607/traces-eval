"""Download the columns the fairness check needs, for every Scale-SWE task (from HF's parquet copy)."""

import os

import duckdb

SRC = "hf://datasets/AweAI-Team/Scale-SWE@~parquet/default/train/*.parquet"
con = duckdb.connect()
if os.environ.get("HF_TOKEN"):  # higher Hugging Face rate limits
    con.execute("CREATE SECRET hf (TYPE huggingface, TOKEN ?)", [os.environ["HF_TOKEN"]])
con.execute(f"""
    COPY (SELECT instance_id, repo, language, problem_statement, patch, f2p_script, f2p_patch, FAIL_TO_PASS
          FROM read_parquet('{SRC}'))
    TO 'data/scaleswe.parquet' (FORMAT parquet)
""")
print(con.execute("SELECT count(*), count(DISTINCT instance_id) FROM 'data/scaleswe.parquet'").fetchone())
print(con.execute("""SELECT language, count(*) FROM 'data/scaleswe.parquet' GROUP BY 1 ORDER BY 2 DESC LIMIT 6""").fetchall())
print("our 60 tasks found:", con.execute("""
    SELECT count(DISTINCT s.instance_id) FROM 'data/scaleswe.parquet' s
    JOIN (SELECT DISTINCT instance_id FROM 'data/sample_index.parquet') i USING (instance_id)""").fetchone()[0])
