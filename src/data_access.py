from __future__ import annotations

import duckdb
import pandas as pd
from pathlib import Path
from typing import Iterable, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "processed" / "credit_risk.duckdb"

def load_features(columns: Optional[Iterable[str]] = None) -> pd.DataFrame:
    """ 
    Load features columns from v_features into a pandas DataFrame
    """
    con =  duckdb.connect(str(DB_PATH), read_only = True)

    if columns is None:
        query =  "SELECT * from v_features"
    else:
        cols = ", ".join(columns)
        query = f"SELECT {cols} FROM v_features"
    
    df = con.execute(query).df()
    con.close()
    return df