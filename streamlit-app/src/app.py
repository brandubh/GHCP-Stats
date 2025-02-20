import streamlit as st
import subprocess
import os
from utils.import_ghcp import import_metrics
from dotenv import load_dotenv

def main():
    st.title("My Streamlit App")
    st.write("Welcome to my Streamlit application!")
    load_dotenv()
    # Add your Streamlit components here
    if st.button("Import Data"):
        import_metrics()
    
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