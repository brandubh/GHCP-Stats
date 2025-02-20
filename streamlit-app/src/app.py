import streamlit as st
import subprocess
import os
from utils.import_ghcp import import_metrics
from utils.helpers import get_data_range
from dotenv import load_dotenv

def main():
    st.title("GitHub Copilot Statistics")
    load_dotenv()
    
    # Show data range information
    min_date, max_date = get_data_range()
    if min_date and max_date:
        st.info(f"📊 Data available from {min_date} to {max_date}")
    
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
    main()