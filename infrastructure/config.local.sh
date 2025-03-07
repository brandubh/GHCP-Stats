    #!/bin/bash
    
    # Source the .env.local file to load environment variables
    source ../app/.env.local

    # Set secrets in key vault using values from .env.local
    az keyvault secret set --vault-name $KEY_VAULT_NAME \
        --name "AZURE-APP-CLIENT-ID" \
        --value "$AZURE_APP_CLIENT_ID"

    az keyvault secret set --vault-name $KEY_VAULT_NAME \
        --name "AZURE-APP-CLIENT-SECRET" \
        --value "$AZURE_APP_CLIENT_SECRET"

    az keyvault secret set --vault-name $KEY_VAULT_NAME \
        --name "AZURE-TENANT-ID" \
        --value "$AZURE_TENANT_ID"

    az keyvault secret set --vault-name $KEY_VAULT_NAME \
        --name "GHCP-TOKEN" \
        --value "$GHCP_TOKEN"  
   
   az containerapp update \
     --name ghcp-stats-app \
     --resource-group ghcp-stats-prod-rg \
     --set-env-vars \
       "KEY_VAULT_NAME=ghcp-stats-kv" \
       "DB_NAME=./app/data/metrics.db"