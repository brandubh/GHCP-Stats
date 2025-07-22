# Dependencies

The project relies on a small set of Python packages and a few external services.

## External services

- **GitHub REST API** – used to download Copilot metrics.
- **Azure Active Directory** – handles user authentication via MSAL.
- **Azure Key Vault** (optional) – can store the GitHub API token when running in Azure.

## Python packages

Versions are defined in `app/requirements.txt`.

- streamlit
- pandas
- numpy
- altair
- requests
- python-dotenv
- streamlit-aggrid
- azure-identity
- azure-keyvault-secrets
- msal

## Development tools

- Docker for building a container image.
- Azure CLI and Bicep for optional Azure deployment.
