import streamlit as st
import os
from dotenv import load_dotenv
from utils.auth_wrapper import require_auth
from pages._loader import loader

# Configure page settings
st.set_page_config(
    page_title="GitHub Copilot Stats",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables at startup
if os.path.exists('.env.local'):
    load_dotenv('.env.local')
elif os.path.exists('app/.env.local'):
    load_dotenv('app/.env.local')
else:
    load_dotenv()

# Initialize session state for authentication
if 'token' not in st.session_state:
    st.session_state['token'] = None

@require_auth
def main():
    # After authentication, load the main dashboard
    loader()

# Debug authentication state
if st.sidebar.checkbox("Debug Auth"):
    st.sidebar.write("Session State:")
    st.sidebar.write({
        "token": "Present" if st.session_state.get('token') else "None",
        "auth_state": st.session_state.get('auth_state'),
        "query_params": dict(st.query_params)
    })
    if st.sidebar.button("Clear Auth State"):
        for key in ['token', 'auth_state', 'error_details']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
        
if __name__ == "__main__":
    main()