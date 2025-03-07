#!/bin/bash

# Read parameters from parameters.prod.json
ENVIRONMENT_NAME=$(jq -r '.parameters.environmentName.value' parameters.prod.json)
LOCATION=$(jq -r '.parameters.location.value' parameters.prod.json)
APP_NAME=$(jq -r '.parameters.appName.value' parameters.prod.json)
ACR_NAME=$(jq -r '.parameters.acrName.value' parameters.prod.json)

# Set resource group name based on parameters
RESOURCE_GROUP="${APP_NAME}-${ENVIRONMENT_NAME}-rg"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Deploy ACR using Bicep
az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file acr.bicep \
  --parameters @parameters.prod.json \
  --only-show-errors

# Authenticate with ACR
az acr login --name $ACR_NAME

# Build and push Docker image with platform specified as linux/amd64
cd ../app  # Navigate to app directory relative to infrastructure folder
docker buildx create --use --name multiarch --driver docker-container
docker buildx build --platform linux/amd64 -t ghcp-stats:latest --load .

ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer --output tsv)
docker tag ghcp-stats:latest $ACR_LOGIN_SERVER/ghcp-stats:latest
docker push $ACR_LOGIN_SERVER/ghcp-stats:latest
cd ../infrastructure  # Return to infrastructure directory

# Deploy Container App using Bicep
az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file main.bicep \
  --parameters @parameters.prod.json \
  --only-show-errors

# Set environment variables from .env file
echo "Setting environment variables from .env file..."
ENV_VARS=""
while IFS= read -r line || [[ -n "$line" ]]; do
    # Skip empty lines and comments
    if [[ -z "$line" ]] || [[ "$line" =~ ^# ]]; then
        continue
    fi
    
    # Extract key and value
    key=$(echo "$line" | cut -d '=' -f 1)
    value=$(echo "$line" | cut -d '=' -f 2-)
    
    # Append to env vars string
    if [[ -z "$ENV_VARS" ]]; then
        ENV_VARS="\"$key=$value\""
    else
        ENV_VARS="$ENV_VARS \"$key=$value\""
    fi
done < "../app/.env"

# Update container app with environment variables
if [[ -n "$ENV_VARS" ]]; then
    echo "Updating Container App with environment variables..."
    eval "az containerapp update \
      --name ${containerAppName:-${APP_NAME}-app} \
      --resource-group $RESOURCE_GROUP \
      --set-env-vars $ENV_VARS"
fi

echo "Deployment completed successfully!"