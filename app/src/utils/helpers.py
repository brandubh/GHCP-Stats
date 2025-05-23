import sqlite3
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import pandas as pd

# --- Database Setup ---

def get_connection():
    """
    Get a connection to the SQLite database with improved error handling.
    Returns a connection object if successful or raises an exception with detailed error info.
    """
    try:
        # Load environment variables if not already loaded
        load_dotenv()
        
        # Get database name from environment variables with fallback
        db_name = os.getenv("DB_NAME", "metrics.db")
        
        # Log current working directory for debugging
        cwd = os.getcwd()
        print(f"Current working directory: {cwd}")
        
        # Full path to database file
        db_path = os.path.join(cwd, db_name)
        
        # Check if database directory exists
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            print(f"Created directory: {db_dir}")
        
        # Check if database file exists (will be created if not)
        file_exists = os.path.isfile(db_path)
        print(f"Database file '{db_path}' exists: {file_exists}")
        
        # Create connection
        conn = sqlite3.connect(db_path, check_same_thread=False)
        
        # Create table if it doesn't exist
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='metrics'")
        if not cursor.fetchone():
            print(f"Creating metrics table in database: {db_path}")
            cursor.execute(
                """
                CREATE TABLE metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    org TEXT,
                    date TEXT,
                    data TEXT
                )
                """
            )
            conn.commit()
            print("Table 'metrics' created successfully")
        
        return conn
    
    except sqlite3.Error as e:
        error_msg = f"SQLite error: {str(e)}"
        print(f"Database connection error: {error_msg}")
        raise Exception(f"Failed to connect to database: {error_msg}")
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"Error in get_connection(): {error_msg}")
        raise Exception(f"Database connection failed: {error_msg}")

def get_data_range():
    """Get the earliest and latest dates from the metrics database."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT MIN(date), MAX(date) FROM metrics")
    min_date, max_date = cur.fetchone()
    conn.close()
    return min_date, max_date

# --- Data Loading & Aggregation ---
def load_metrics(date_range, orgs):
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT org, date, data FROM metrics WHERE date BETWEEN ? AND ?"
    params = [date_range[0].isoformat(), date_range[1].isoformat()]
    if orgs:
        placeholders = ",".join("?" for _ in orgs)
        query += f" AND org IN ({placeholders})"
        params.extend(orgs)
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    records = []
    for org, rec_date, data in rows:
        records.append({"org": org, "date": rec_date, "data": json.loads(data)})
    return records

def get_org_options():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT org FROM metrics")
    orgs = sorted([row[0] for row in cur.fetchall()])
    conn.close()
    return orgs

def get_filter_options(records):
    editors, models, languages = set(), set(), set()
    for rec in records:
        comp = rec["data"].get("copilot_ide_code_completions")
        if comp:
            for editor in comp.get("editors", []):
                editors.add(editor.get("name"))
                for model in editor.get("models", []):
                    models.add(model.get("name"))
                    for lang in model.get("languages", []):
                        languages.add(lang.get("name"))
    return sorted(editors), sorted(models), sorted(languages)

def build_dataframe(records, sel_editors, sel_models, sel_languages):
    rows = []
    for rec in records:
        dt = datetime.strptime(rec["date"], "%Y-%m-%d").date()
        data = rec["data"]
        active = data.get("total_active_users", 0)
        engaged = data.get("total_engaged_users", 0)
        inactive = active - engaged
        sug, acc = record_code_metrics(rec, sel_editors, sel_models, sel_languages)
        rate = (acc / sug * 100) if sug else 0
        rows.append({
            "date": dt,
            "org": rec["org"],
            "active": active,
            "engaged": engaged,
            "inactive": inactive,
            "suggested": sug,
            "accepted": acc,
            "acceptance_rate": rate
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df.sort_values("date", inplace=True)
    return df

def record_code_metrics(record, sel_editors, sel_models, sel_languages):
    suggested = 0
    accepted = 0
    comp = record["data"].get("copilot_ide_code_completions")
    if comp:
        for editor in comp.get("editors", []):
            if sel_editors and editor.get("name") not in sel_editors:
                continue
            for model in editor.get("models", []):
                if sel_models and model.get("name") not in sel_models:
                    continue
                for lang in model.get("languages", []):
                    if sel_languages and lang.get("name") not in sel_languages:
                        continue
                    suggested += lang.get("total_code_lines_suggested", 0)
                    accepted += lang.get("total_code_lines_accepted", 0)
    return suggested, accepted

def load_code_metrics(records, sel_editors, sel_models, sel_languages):
    # Get language data from records
    language_stats = {}
    for record in records:
        completions = record["data"].get("copilot_ide_code_completions", {})
        if completions and "editors" in completions:
            for editor in completions["editors"]:
                if sel_editors and editor.get("name") not in sel_editors:
                    continue
                for model in editor.get("models", []):
                    if sel_models and model.get("name") not in sel_models:
                        continue
                    for lang in model.get("languages", []):
                        if sel_languages and lang.get("name") not in sel_languages:
                            continue
                        lang_name = lang.get("name", "Unknown")
                        suggested = lang.get("total_code_lines_suggested", 0)
                        accepted = lang.get("total_code_lines_accepted", 0)
                        
                        if lang_name not in language_stats:
                            language_stats[lang_name] = {"suggested": 0, "accepted": 0}
                        
                        language_stats[lang_name]["suggested"] += suggested
                        language_stats[lang_name]["accepted"] += accepted

    # Create DataFrame for visualization
    data = []
    for lang, stats in language_stats.items():
        if stats["suggested"] > 0:  # Only include languages with suggestions
            acceptance_rate = (stats["accepted"] / stats["suggested"]) * 100
            data.append({
                "Language": lang,
                "Acceptance Rate": acceptance_rate,
                "Suggested Lines": stats["suggested"],
                "Accepted Lines": stats["accepted"]
            })

    df = pd.DataFrame(data)
    df = df.sort_values("Suggested Lines", ascending=False)
    return df