import streamlit as st
import functools
from utils.auth import validate_token, handle_redirect

def require_auth(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Check for auth code in URL parameters first
        query_params = st.query_params
        if "code" in query_params:
            handle_redirect()
            # After handling redirect, we should have a token or an error
            # The handle_redirect function will call st.rerun() if successful
        
        # Validate token if we have one
        if st.session_state.get('token'):
            # We have a token, validate it
            is_authenticated = validate_token()
            
            # If authenticated, run the wrapped function
            if is_authenticated:
                return func(*args, **kwargs)
        else:
            # No token, validate_token will show login button and st.stop()
            validate_token()
    
    return wrapper