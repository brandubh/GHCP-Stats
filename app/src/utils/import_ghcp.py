import requests
import json
from dotenv import load_dotenv
import os
import streamlit as st
from utils.helpers import get_connection
from utils.auth import get_secret

def import_metrics_for_org(org, token):
    url = f"https://api.github.com/orgs/{org}/copilot/metrics"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    metrics = []
    while url:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            metrics.extend(resp.json())
            # Check for pagination
            if 'Link' in resp.headers:
                links = resp.headers['Link']
                next_link = None
                for link in links.split(','):
                    if 'rel="next"' in link:
                        next_link = link[link.find('<') + 1:link.find('>')]
                        break
                url = next_link
            else:
                url = None
        else:
            st.error(f"Error fetching metrics for {org}: {resp.status_code}")
            break
    return metrics

def store_metrics(org, metrics):
    # TODO: if running on Azure copy the datbase file from persistent storage to the local storage
    # and then copy it back to the persistent storage after the import
    # the database file is stored in the DB_NAME environment variable
    # the persistent storage is stored in the PERSISTENT_STORAGE environment variable
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
    org_list = [org.strip() for org in os.getenv("ORG_LIST", "").split(",") if org.strip()]
    token = os.getenv("GHCP_TOKEN")
    if not token:
        token = get_secret("GHCP_TOKEN")
    if not token:
        st.error("GitHub token not found in .env file.")
        st.stop()
    for org in org_list:
        metrics = import_metrics_for_org(org, token)
        store_metrics(org, metrics)
