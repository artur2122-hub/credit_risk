from pathlib import Path
import duckdb


PROJECT = Path("/data/ds/projects/credit-risk-prediction")
DB_PATH = PROJECT / "/data/processed/credit_risk.duckdb"
PARQUET = PROJECT / 'data/processed/default_clients.parquet'

con = duckdb.connect(str(DB_PATH))

con.execute("""
CREATE OR REPLACE TABLE raw_defaults_clients AS            
SELECT * FROM read_parquet(?)       
""", [str(PARQUET)])

n = con.execute("SELECT COUNT(*) FROM raw_defaults_clients").fetchone()[0]
print("DB: ", DB_PATH)
print("Table: raw_default_clients")
print("Rows:",n)

con.close()
