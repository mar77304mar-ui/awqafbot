import sqlite3
import pandas as pd
from config import DB

def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("CREATE TABLE IF NOT EXISTS data (raw TEXT)")
    conn.commit()
    conn.close()

def save_excel(df):
    conn = sqlite3.connect(DB)
    df.to_sql("data", conn, if_exists="replace", index=False)
    conn.close()

def search_all(keyword):
    conn = sqlite3.connect(DB)
    df = pd.read_sql("SELECT * FROM data", conn)
    conn.close()

    if df.empty:
        return df

    mask = df.astype(str).apply(lambda x: x.str.contains(keyword, case=False, na=False))
    return df[mask.any(axis=1)].head(10)

def get_stats():
    conn = sqlite3.connect(DB)
    df = pd.read_sql("SELECT * FROM data", conn)
    conn.close()

    return {
        "rows": len(df),
        "cols": len(df.columns),
        "columns": list(df.columns)
    }
