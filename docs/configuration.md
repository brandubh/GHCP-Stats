# Configuration

The application is configured entirely through environment variables. During local development these can be placed in an `.env` or `.env.local` file. The following variables are recognised:

| Variable | Purpose |
|----------|---------|
| `ORG_LIST` | Comma separated list of organisations to query |
| `GHCP_TOKEN` | GitHub token with access to the Copilot metrics API |
| `DB_NAME` | Path to the SQLite database file (default `metrics.db`) |
| `PERSISTENT_STORAGE` | Optional path to a database file on a mounted volume |
| `AZURE_APP_CLIENT_ID` | Azure AD application (client) ID |
| `AZURE_APP_CLIENT_SECRET` | Client secret for the app registration |
| `AZURE_TENANT_ID` | Azure tenant ID |
| `KEY_VAULT_NAME` | Name of the Azure Key Vault containing secrets |
| `REDIRECT_BASE_URL` | Base URL used for OAuth redirects |

Only `ORG_LIST` and `GHCP_TOKEN` are required for local use. When deployed to Azure, authentication variables and optionally `KEY_VAULT_NAME` must also be provided. If `PERSISTENT_STORAGE` is set the import routine copies the database to this location before and after each update.
