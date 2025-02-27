import streamlit as st
import os
from dotenv import load_dotenv
from utils.auth_wrapper import require_auth

# Load environment variables at startup
if os.path.exists('app/.env.local'):
    load_dotenv('app/.env.local')
else:
    load_dotenv()

@require_auth
def main():
    st.title("GitHub Copilot Statistics")
    st.write("Welcome to the GitHub Copilot Statistics Dashboard")
    st.write("Please select a page from the sidebar to view different metrics.")

if __name__ == "__main__":
    main()