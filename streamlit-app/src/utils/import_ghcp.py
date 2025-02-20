import requests
import json
from dotenv import load_dotenv
import os
import streamlit as st  # Add this missing import
# Change from relative to absolute import
from utils.helpers import get_connection



# --- Backend Import Routine ---
def import_metrics_for_org(org, token):
    url = f"https://api.github.com/orgs/{org}/copilot/metrics"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return resp.json()
    else:
        st.error(f"Error fetching metrics for {org}: {resp.status_code}")
        return []

def store_metrics(org, metrics):
    conn = get_connection()
    cur = conn.cursor()
    for metric in metrics:
        rec_date = metric.get("date")
        cur.execute("SELECT id FROM metrics WHERE org=? AND date=?", (org, rec_date))
        if not cur.fetchone():
            cur.execute("INSERT INTO metrics (org, date, data) VALUES (?, ?, ?)",
                        (org, rec_date, json.dumps(metric)))
    conn.commit()
    conn.close()

def import_metrics():
    load_dotenv()
    org_list = [org.strip() for org in os.getenv("ORG_LIST", "").split(",") if org.strip()]
    token = os.getenv("GHCP_TOKEN")
    if not token:
        st.error("GitHub token not found in .env file.")
        st.stop()
    for org in org_list:
        metrics = import_metrics_for_org(org, token)
        store_metrics(org, metrics)
