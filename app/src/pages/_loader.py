import streamlit as st
import subprocess
import os
from datetime import datetime, timedelta
from utils.import_ghcp import import_metrics
from utils.helpers import get_data_range
from dotenv import load_dotenv
from utils.auth_wrapper import require_auth


# Initialize session state for scheduler
def init_session_state():
    if 'scheduler_status' not in st.session_state:
        st.session_state['scheduler_status'] = False
    if 'last_import' not in st.session_state:
        st.session_state['last_import'] = None
    if 'next_scheduled_import' not in st.session_state:
        st.session_state['next_scheduled_import'] = None

def check_scheduled_import():
    """Check if it's time to run the scheduled import"""
    if not st.session_state['scheduler_status']:
        return
        
    now = datetime.now()
    if (st.session_state['last_import'] is None or 
        st.session_state['next_scheduled_import'] is None or 
        now >= st.session_state['next_scheduled_import']):
        import_metrics()
        st.session_state['last_import'] = now
        # Schedule next import for tomorrow at the same time
        st.session_state['next_scheduled_import'] = now + timedelta(days=1)
        st.rerun()

@require_auth
def loader():
    st.title("GitHub Copilot Statistics")
    
    # Initialize session state for scheduler
    init_session_state()
    
    # Check for scheduled imports
    check_scheduled_import()
    
    # Show data range information
    min_date, max_date = get_data_range()
    if min_date and max_date:
        st.info(f"📊 Data available from {min_date} to {max_date}")
    
    # Add scheduler control
    scheduler_enabled = st.checkbox(
        "Enable Daily Auto-Import", 
        value=st.session_state['scheduler_status'],
        help="Automatically import new data once per day"
    )
    
    if scheduler_enabled != st.session_state['scheduler_status']:
        st.session_state['scheduler_status'] = scheduler_enabled
        if scheduler_enabled:
            # Schedule first import
            st.session_state['next_scheduled_import'] = datetime.now() + timedelta(days=1)
        st.rerun()
    
    # Show scheduler status
    if st.session_state['scheduler_status']:
        st.caption("Auto-import is enabled")
        if st.session_state['last_import']:
            st.caption(f"Last import: {st.session_state['last_import'].strftime('%Y-%m-%d %H:%M:%S')}")
        if st.session_state['next_scheduled_import']:
            st.caption(f"Next import scheduled for: {st.session_state['next_scheduled_import'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Manual import button
    if st.button("Import Data Now"):
        import_metrics()
        st.session_state.last_import = datetime.now()
        min_date, max_date = get_data_range()
        st.rerun()
    
    # Add your Streamlit components here
    if st.button("Import Data"):
        import_metrics()
        # Refresh date range after import
        min_date, max_date = get_data_range()
        st.rerun()
    
    if st.button("Export Database"):
        db_path = os.getenv("DB_NAME", "metrics.db")
        if os.path.exists(db_path):
            db_dump = subprocess.check_output(["sqlite3", db_path, ".dump"], text=True)
            st.download_button("Download Database", db_dump, file_name="database.sql", mime="text/plain")
        else:
            st.error("Database file not found.")

    if st.button("Import Database From Export"):
        uploaded_file = st.file_uploader("Upload .sql file", type=["sql"])
        if uploaded_file is not None:
            with open("imported.sql", "wb") as f:
                f.write(uploaded_file.getbuffer())
            subprocess.run(["sqlite3", os.getenv("DB_NAME", "metrics.db"), ".read imported.sql"])
            st.success("Database imported successfully!")
            
if __name__ == "__main__":
    loader()