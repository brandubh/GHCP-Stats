# Security

Authentication is handled via Azure Active Directory. `utils/auth.py` uses the MSAL library to perform an OAuth2 authorization code flow. When a user accesses the app without a valid token they are redirected to the Azure login page. The resulting access token is stored in the Streamlit session state.

Secrets such as the GitHub token can be stored in Azure Key Vault. `utils/auth.get_secret` retrieves them using `DefaultAzureCredential` when running in Azure, otherwise environment variables are used.

No API keys or user credentials are stored in the repository.
