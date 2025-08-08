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

def import_metrics() -> None:
    """
    Imports metrics for all organizations listed in the ORG_LIST environment variable.
    If running on Azure, copies the database file from persistent storage to local storage before import,
    and back to persistent storage after import.

    Notes:
        Displays an error message and stops execution if the GitHub token is not found.
    """
    import shutil
    import logging

    org_list = [org.strip() for org in os.getenv("ORG_LIST", "").split(",") if org.strip()]
    token = os.getenv("GHCP_TOKEN")
    if not token:
        token = get_secret("GHCP_TOKEN")
    if not token:
        st.error("GitHub token not found in .env file.")
        st.stop()

    local_db_path = os.getenv("DB_NAME")
    persistent_db_path = os.getenv("PERSISTENT_STORAGE")
    running_on_azure = bool(persistent_db_path and local_db_path and os.path.exists(persistent_db_path))

    # If running on Azure, copy DB from persistent storage to local
    if running_on_azure and os.path.exists(persistent_db_path):
        try:
            shutil.copy2(persistent_db_path, local_db_path)
            logging.info(f"Copied DB from {persistent_db_path} to {local_db_path}")
        except Exception as exc:
            st.error(f"Failed to copy DB from persistent storage: {exc}")
            st.stop()

    for org in org_list:
        metrics = import_metrics_for_org(org, token)
        store_metrics(org, metrics)

    # After import, copy DB back to persistent storage if on Azure
    if running_on_azure:
        try:
            shutil.copy2(local_db_path, persistent_db_path)
            logging.info(f"Copied DB back to {persistent_db_path}")
        except Exception as exc:
            st.error(f"Failed to copy DB back to persistent storage: {exc}")
            st.stop()
