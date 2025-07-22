import os
import json
import logging
import requests
from .config import settings
from .database import get_session
from .db import models


def import_metrics_for_org(org: str, token: str):
    url = f"https://api.github.com/orgs/{org}/copilot/metrics"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    metrics = []
    while url:
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            logging.error("Error fetching metrics for %s: %s", org, resp.text)
            break
        metrics.extend(resp.json())
        next_url = None
        if 'Link' in resp.headers:
            for link in resp.headers['Link'].split(','):
                if 'rel="next"' in link:
                    next_url = link[link.find('<') + 1:link.find('>')]
                    break
        url = next_url
    return metrics


def store_metrics(org: str, metrics: list):
    session = get_session()
    try:
        for metric in metrics:
            rec_date = metric.get("date")
            existing = session.query(models.Metric).filter_by(org=org, date=rec_date).first()
            if not existing:
                m = models.Metric(org=org, date=rec_date, data=json.dumps(metric))
                session.add(m)
        session.commit()
    finally:
        session.close()


def import_metrics() -> None:
    org_list = [o.strip() for o in settings.org_list.split(',') if o.strip()]
    token = settings.github_token
    if not token:
        raise RuntimeError("GitHub token not configured")

    for org in org_list:
        metrics = import_metrics_for_org(org, token)
        if metrics:
            store_metrics(org, metrics)
