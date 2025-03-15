from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import streamlit as st
from msal import ConfidentialClientApplication
import os
import logging
from typing import Optional, Tuple, Any, Dict
import requests

# Set up logging

# Get logging level from environment variable, default to INFO
log_level_name = os.getenv("LOG_LEVEL", "DEBUG").upper()
log_level = getattr(logging, log_level_name, logging.INFO)

# Configure logging
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Log startup information
logger.info(f"Authentication module initialized with log level: {log_level_name}")

def get_secret(secret_name: str) -> Optional[str]:
    """
    Retrieve secret from Azure KeyVault with local development support.
    
    Args:
        secret_name: Name of the secret to retrieve
        
    Returns:
        The secret value if found, None otherwise
        
    Note:
        Follows a fallback chain: environment variables -> KeyVault -> 
        Streamlit secrets -> environment variables with direct name
    """
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
        client_id = os.getenv("AZURE_CLIENT_ID")
        identity_endpoint = os.getenv("IDENTITY_ENDPOINT")
        
        logger.info(f"Attempting to authenticate with Key Vault {key_vault_name}")
        logger.info(f"AZURE_CLIENT_ID available: {client_id is not None}")
        logger.info(f"IDENTITY_ENDPOINT available: {identity_endpoint is not None}")
        
        # # For Container Apps, use ManagedIdentityCredential explicitly
        # from azure.identity import ManagedIdentityCredential, DefaultAzureCredential
        
        # # Try with specific client ID if available
        # if client_id:
        #     logger.info(f"Using ManagedIdentityCredential with client_id: {client_id[:8]}...")
        #     credential = ManagedIdentityCredential(client_id=client_id)
        # else:
        #     # Fall back to default credential
        #     logger.info("Using DefaultAzureCredential")
        #     credential = DefaultAzureCredential()
        # Use DefaultAzureCredential which supports multiple authentication methods
        credential = DefaultAzureCredential()
        vault_url = f"https://{key_vault_name}.vault.azure.net/"
        client = SecretClient(vault_url=vault_url, credential=credential)
        return client.get_secret(secret_name_formatted).value
    except Exception as e:
        # Get credential identity information when possible
        credential_id = "unknown"
        try:
            # Try to extract identity information from credential
            if hasattr(credential, 'get_token'):
                token_info = credential.get_token("https://vault.azure.net/.default")
                if hasattr(token_info, 'tenant_id') and hasattr(token_info, 'client_id'):
                    credential_id = f"tenant:{token_info.tenant_id[:8]}...client:{token_info.client_id[:8]}..."
                    
        except Exception as token_error:
            logger.error(f"Error getting token info: {str(token_error)}")
            
        # Use warning for UI and log the detailed error
        st.warning(f"Could not retrieve secret '{secret_name_formatted}' from Key Vault '{key_vault_name}' using credential '{credential_id}'")
        logger.error(f"KeyVault error details: {str(e)}")
        # Dump all environment variables for debugging
        env_vars = {key: value for key, value in os.environ.items()}
        st.warning(f"Environment variables: {env_vars}")
        
        identity_header = os.getenv("IDENTITY_HEADER")

        if identity_endpoint and identity_header:
            try:
                response = requests.get(
                    f"{identity_endpoint}?resource=https://vault.azure.net&api-version=2019-08-01",
                    headers={"X-IDENTITY-HEADER": identity_header}
                )
                st.warning(f"Token response: {response.json()}")
            except Exception as e:
                st.warning(f"Token request failed: {str(e)}")
        else:
            st.warning("Managed identity environment variables are missing.")
        # For debugging managed identity availability in Azure
        logger.debug(f"IDENTITY_ENDPOINT: {os.getenv('IDENTITY_ENDPOINT')}")
        logger.debug(f"IDENTITY_HEADER: {os.getenv('IDENTITY_HEADER')}")
        
        
        # For local development, fallback to secrets.toml if it exists
        if hasattr(st, 'secrets') and secret_name in st.secrets:
            return st.secrets[secret_name]
        
        # Final fallback to environment variables with direct name
        return os.getenv(secret_name)

def init_auth() -> Tuple[ConfidentialClientApplication, str]:
    """
    Initialize authentication components.
    
    Returns:
        Tuple containing:
            - MSAL ConfidentialClientApplication instance
            - Redirect URI for authentication
    """
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

def validate_token() -> bool:
    """
    Validate current token or redirect to login.
    
    Returns:
        True if a valid token exists, otherwise redirects and returns False
    """
    # Only show debug info in development
    if os.getenv("ENVIRONMENT") == "development":
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

def handle_redirect() -> None:
    """
    Handle the redirect from Azure AD with the authorization code.
    
    This function processes the authentication code received after user login,
    acquires the access token, and stores it in the session state.
    """
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