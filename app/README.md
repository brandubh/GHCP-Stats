# README.md

# GitHub Copilot Statistics App

This is a Streamlit application that provides an interactive web interface for data visualization and analysis.

## Project Structure

```
app
├── src
│   ├── app.py          # Main entry point of the Streamlit application
│   ├── pages
│   │   └── page1.py    # Additional page in the Streamlit app
│   └── utils
│       └── helpers.py   # Utility functions for the application
├── data
│   └── .gitkeep        # Keeps the data directory tracked by Git
├── requirements.txt     # Python packages required for the app
├── .gitignore           # Files and directories to be ignored by Git
└── README.md            # Documentation for the project
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd streamlit-app
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

To run the Streamlit application, use the following command:

```
streamlit run src/app.py
```

## Azure Deployment

### Prerequisites

- Azure CLI
  ```bash
  brew install azure-cli
  ```
- Docker
  ```bash
  brew install docker
  ```
- Azure subscription with admin access
- Access to Azure Entra ID with admin privileges

### 1. App Registration in Entra ID

1. Go to Azure Portal > Microsoft Entra ID:
   - Select "App registrations" from the left menu
   - Click "New registration"

2. Register the application:
   - **Name**: "GHCP Stats"
   - **Supported account types**: Select "Accounts in this organizational directory only (Single tenant)"
   - **Platform configuration**: Select "Web"
   - **Redirect URI**: For local development, use exactly `http://localhost:8501` (no trailing slash)
   - Click "Register"

3. Configure authentication:
   - Go to "Authentication" in the left menu
   - Under "Platform configurations":
     - Verify the Web platform is configured
     - For production, add `https://<your-app-name>.azurecontainer.io` (no trailing slash)
   - Under "Implicit grant and hybrid flows":
     - ✅ Check "Access tokens (used for implicit flows)"
     - ✅ Check "ID tokens (used for implicit and hybrid flows)"
   - Under "Advanced settings":
     - Set "Allow public client flows" to "No"
     - Set "Enable the following mobile and desktop flows" to "No"
   - Click "Save"

4. Configure token settings:
   - Go to "Token configuration" in the left menu
   - Click "Add optional claim"
   - Add the following claims to the Access token:
     - `email`
     - `preferred_username`
   - Click "Add"

5. Configure API permissions:
   - Go to "API permissions" in the left menu
   - Click "Add a permission"
   - Select "Microsoft Graph"
   - Select "Delegated permissions"
   - Add these permissions:
     - `User.Read` (default)
     - `email`
     - `offline_access` (for refresh tokens)
     - `profile`
   - Click "Add permissions"
   - Click "Grant admin consent" button (requires admin)

6. Create client secret:
   - Go to "Certificates & secrets" in the left menu
   - Under "Client secrets":
     - Click "New client secret"
     - Description: "GHCP Stats App Secret"
     - Expires: Select appropriate duration (e.g., "12 months")
     - Click "Add"
   - ⚠️ **IMPORTANT**: Copy the secret value immediately - it won't be shown again

7. Required configuration values:
   ```
   Application (client) ID: Found in Overview
   Directory (tenant) ID: Found in Overview
   Client Secret: Value copied in step 6
   Redirect URI: http://localhost:8501 (development)
                https://<your-app-name>.azurecontainer.io (production)
   ```

8. Update environment variables:
   ```bash
   # Local development (.env.local)
   AZURE_CLIENT_ID="your-client-id"
   AZURE_APP_CLIENT_SECRET="your-client-secret"
   AZURE_TENANT_ID="your-tenant-id"
   REDIRECT_BASE_URL="http://localhost:8501"
   ```

### Important Security Notes:

- Redirect URIs must match exactly (no trailing slashes)
- Never commit secrets to version control
- Use managed identities in production when possible
- Store secrets in Azure Key Vault
- Implement token refresh logic
- Monitor token expiration
- Review permissions regularly
- Implement proper error handling for auth failures

### 2. Infrastructure Deployment

1. Create Azure resources using Bicep:
   ```bash
   # Login to Azure
   az login

   # Create deployment
   cd infrastructure
   chmod +x deploy.sh
   ./deploy.sh
   ```

2. Configure Key Vault secrets:
   ```bash
   az keyvault secret set --vault-name <vault-name> \
     --name "APP-CLIENT-ID" \
     --value "your-client-id"

   az keyvault secret set --vault-name <vault-name> \
     --name "APP-CLIENT-SECRET" \
     --value "your-client-secret"

   az keyvault secret set --vault-name <vault-name> \
     --name "TENANT-ID" \
     --value "your-tenant-id"

   az keyvault secret set --vault-name <vault-name> \
     --name "GHCP-TOKEN" \
     --value "your-github-token"
   ```

### 3. Container Image Build and Push

1. Build the Docker image:
   ```bash
   docker build -t ghcp-stats:latest .
   ```

2. Push to Azure Container Registry:
   ```bash
   # Login to ACR
   az acr login --name <registry-name>

   # Tag image
   docker tag ghcp-stats:latest <registry-name>.azurecr.io/ghcp-stats:latest

   # Push image
   docker push <registry-name>.azurecr.io/ghcp-stats:latest
   ```

### 4. Container App Configuration

1. Update Container App with environment variables:
   ```bash
   az containerapp update \
     --name ghcp-stats-app \
     --resource-group ghcp-stats-rg \
     --set-env-vars \
       "AZURE_CLIENT_ID=your-client-id" \
       "AZURE_TENANT_ID=your-tenant-id" \
       "KEY_VAULT_NAME=your-keyvault-name" \
       "DB_NAME=/app/data/metrics.db"
   ```

2. Configure authentication:
   - Go to Container App > Authentication
   - Add identity provider:
     - Provider: Microsoft
     - Tenant type: Workplace
     - Client ID: (from app registration)
     - Client secret: (from app registration)
     - Issuer URL: `https://login.microsoftonline.com/<tenant-id>/v2.0`
   - Configure redirect URIs
   - Enable session management

### 5. Data Storage Configuration

The application uses Azure Files for persistent SQLite storage:

1. Verify file share:
   ```bash
   az storage share show \
     --name ghcpstatsdata \
     --account-name <storage-account-name>
   ```

2. Monitor data persistence:
   ```bash
   az storage file list \
     --share-name ghcpstatsdata \
     --account-name <storage-account-name>
   ```

### 6. Verify Deployment

1. Access the application:
   ```
   https://ghcp-stats-app.<region>.azurecontainer.io
   ```

2. Check logs:
   ```bash
   az containerapp logs show \
     --name ghcp-stats-app \
     --resource-group ghcp-stats-rg \
     --follow
   ```

### Environment Variables

Required environment variables for the application:

| Variable | Description | Source |
|----------|-------------|--------|
| AZURE_CLIENT_ID | App registration client ID | Entra ID |
| AZURE_TENANT_ID | Azure tenant ID | Entra ID |
| KEY_VAULT_NAME | Name of Azure Key Vault | Infrastructure |
| DB_NAME | SQLite database path | Container configuration |
| GHCP_TOKEN | GitHub Copilot API token | Key Vault |

### Troubleshooting

- **Authentication Issues**: Verify app registration and redirect URIs
- **Data Persistence**: Check Azure Files mount and permissions
- **Container Startup**: Review container logs and environment variables
- **Key Vault Access**: Verify managed identity assignments

## Contributing

Feel free to submit issues or pull requests for any improvements or bug fixes.