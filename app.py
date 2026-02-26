
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date, timedelta
import difflib

DB_PATH = "rca.db"

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS rcas (
        rca_id TEXT PRIMARY KEY,
        oem TEXT,
        environment TEXT,
        title TEXT,
        root_cause TEXT,
        created_at TEXT
    );
    """)
    conn.commit()
    conn.close()

def qdf(sql):
    conn = get_conn()
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df

def top_similar_rcas(query_text, topk=5):
    rcas = qdf("SELECT * FROM rcas")
    if rcas.empty:
        return pd.DataFrame()

    rcas["combined"] = rcas["title"].fillna("") + " " + rcas["root_cause"].fillna("")
    scores = []

    for text in rcas["combined"]:
        score = difflib.SequenceMatcher(None, query_text.lower(), text.lower()).ratio()
        scores.append(score)

    rcas["similarity"] = scores
    return rcas.sort_values("similarity", ascending=False).head(topk)

st.set_page_config(page_title="RCA Dashboard Light", layout="wide")
init_db()

st.title("RCA Closed-Loop Dashboard (Lightweight Version)")
st.write("AI similarity uses difflib (no heavy ML libraries).")

query = st.text_area("Paste new incident description:")

if st.button("Find Similar RCAs"):
    results = top_similar_rcas(query)
    if results.empty:
        st.info("No RCAs found.")
    else:
        st.dataframe(results)
