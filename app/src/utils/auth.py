from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import streamlit as st
from msal import ConfidentialClientApplication
import os

def get_secret(secret_name):
    """Retrieve secret from Azure KeyVault with local development support"""
    import os
    

    
    # First check if we have a local override (for development)
    local_secret = os.getenv(secret_name)
    if local_secret:
        return local_secret
    
    # Transform underscores to hyphens in secret name
    secret_name_formatted = secret_name.replace("_", "-")
    # Get Key Vault name from environment or streamlit secrets
    key_vault_name = os.getenv("KEY_VAULT_NAME")
    if not key_vault_name:
        st.error("Key Vault name not found in environment variables or streamlit secrets")
        return None
        
    try:
        # Use DefaultAzureCredential which supports multiple authentication methods
        credential = DefaultAzureCredential()
        vault_url = f"https://{key_vault_name}.vault.azure.net/"
        client = SecretClient(vault_url=vault_url, credential=credential)
        return client.get_secret(secret_name_formatted).value
    except Exception as e:
        st.warning(f"Could not retrieve secret from Key Vault: {type(e).__name__}")
        
        # For local development, fallback to secrets.toml if it exists
        if hasattr(st, 'secrets') and secret_name in st.secrets:
            return st.secrets[secret_name]
        
        # Final fallback to environment variables with direct name
        return os.getenv(secret_name)

def init_auth():
    """Initialize authentication"""
    if 'token' not in st.session_state:
        st.session_state['token'] = None
    
    # Azure AD B2C details from env or KeyVault
    client_id = os.getenv("AZURE_APP_CLIENT_ID") or get_secret("AZURE_APP_CLIENT_ID")
    client_secret = os.getenv("AZURE_APP_CLIENT_SECRET") or get_secret("AZURE_APP_CLIENT_SECRET")
    tenant_id = os.getenv("AZURE_TENANT_ID") or get_secret("AZURE_TENANT_ID")
    
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    # Get the base URL dynamically
    base_url = os.getenv("REDIRECT_BASE_URL", "http://localhost:8501")
    redirect_uri = f"{base_url}"  # Redirect URL for the app

    app = ConfidentialClientApplication(
        client_id,
        authority=authority,
        client_credential=client_secret,
    )

    return app, redirect_uri

def validate_token():
    """Validate current token or redirect to login"""
    # Debug the session state
    st.write(f"Debug - Token in session: {'Yes' if st.session_state.get('token') else 'No'}")
    
    if st.session_state.get('token'):
        try:
            app, redirect_uri = init_auth()
            result = app.acquire_token_silent(
                scopes=["User.Read"],
                account=None
            )
            if result:
                st.session_state['token'] = result['access_token']
                st.session_state['auth_state'] = 'authenticated'
                return True
            # Token couldn't be refreshed silently, but we have one
            return True
        except Exception as e:
            st.error(f"Token validation error: {str(e)}")
    
    # No valid token, start authentication
    app, redirect_uri = init_auth()
    auth_url = app.get_authorization_request_url(
        scopes=["User.Read"],
        redirect_uri=redirect_uri
    )
    
    st.markdown(
        f"""
        <div style="text-align: center; margin-top: 50px;">
            <h2>Authentication Required</h2>
            <a href="{auth_url}" target="_self">
                <button style="padding: 10px 20px; cursor: pointer; background-color: #0078d4; color: white; border: none; border-radius: 4px;">
                    Login with Microsoft
                </button>
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.stop()  # Important: Stop execution
    return False

def handle_redirect():
    """Handle the redirect from Azure AD"""
    app, redirect_uri = init_auth()
    query_params = st.query_params
    
    if "code" in query_params:
        try:
            code = query_params["code"]
            result = app.acquire_token_by_authorization_code(
                code,
                scopes=["User.Read"],
                redirect_uri=redirect_uri
            )
            if "access_token" in result:
                st.session_state['token'] = result['access_token']
                st.session_state['auth_state'] = 'authenticated'
                # Clear URL parameters after successful authentication
                st.query_params.clear()  # Use clear() instead of experimental_set_query_params
                st.rerun()
            else:
                st.error("Authentication failed: No access token received")
                st.session_state['auth_state'] = 'error'
        except Exception as e:
            st.error(f"Authentication failed: {str(e)}")
            st.session_state['auth_state'] = 'error'
            st.session_state['error_details'] = str(e)