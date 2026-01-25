import pandas as pd
from pathlib import Path

in_path = Path('/data/ds/datasets/default_clients/default_clients.xls')
out_dir = Path("/data/ds/projects/credit-risk-prediction/data/processed")
out_dir.mkdir(parents =  True, exist_ok = True)

out_parquet = out_dir  / "default_clients.parquet"
out_csv = out_dir / "default_clients.csv"

def main() -> None:
    df = pd.read_excel(in_path)
    #1 Drop excel junk columns likes "Unnamed:0"
    df = df.loc[:, ~df.columns.astype(str).str.match(r"^Unnamed")]
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace(r"\s+", '_', regex=True)
        .str.replace(r"[^\w]+", "_", regex = True)
        .str.replace(r"_+", '_', regex=True)
        .str.strip("_")
    )
    obj_cols = df.select_dtypes(include = ["object"]).columns
    for c in obj_cols:
        df[c] = df[c].astype("string")
    
    df.to_parquet(out_parquet, index = False)
    df.to_csv(out_csv, index = False)

    print('Wrote: ',out_parquet)
    print("Also wrote: ", out_csv)
    print('rows: ', len(df), 'cols: ', df.shape[1])
    print('columns: ', list(df.columns[:]))

if __name__ == "__main__":
    main()