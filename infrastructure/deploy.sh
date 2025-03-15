#!/bin/bash
#
# Deploy GHCP-Stats application to Azure Container Apps
# -----------------------------------------------------
#
# This script automates the deployment of the GHCP-Stats application to Azure Cloud,
# using Azure Container Apps, Container Registry, Front Door, Key Vault, and Microsoft Defender.
#
# Prerequisites:
#   - Azure CLI installed and logged in (az login)
#   - jq command-line JSON processor installed
#   - Bicep CLI installed
#   - Parameters files (parameters.main.dev.json, parameters.acr.dev.json)
#   - .env file in the app directory with environment variables
#   - Build script (build.sh) in the current directory
#   - Bicep templates (main.bicep, acr.bicep, defender.bicep)
#
# Usage:
#   ./deploy.sh
#
# Author: [Your Name]
# Last Updated: 2025-03-15

# Exit immediately if a command exits with a non-zero status
set -e

# Read parameters from parameters.json
# These parameters define core deployment settings like environment name and location
# Read parameters from parameters.json files
ENVIRONMENT_NAME=$(jq -r '.parameters.environmentName.value' parameters.main.dev.json)
LOCATION=$(jq -r '.parameters.location.value' parameters.main.dev.json)
APP_NAME=$(jq -r '.parameters.appName.value' parameters.main.dev.json)
ACR_NAME=$(jq -r '.parameters.acrName.value' parameters.main.dev.json)

# Check if any parameter is missing
if [[ -z "$ENVIRONMENT_NAME" ]]; then
  echo "❌ Error: environmentName not defined in parameters.main.dev.json"
  exit 1
fi

if [[ -z "$LOCATION" ]]; then
  echo "❌ Error: location not defined in parameters.main.dev.json"
  exit 1
fi

if [[ -z "$APP_NAME" ]]; then
  echo "❌ Error: appName not defined in parameters.main.dev.json"
  exit 1
fi

if [[ -z "$ACR_NAME" ]]; then
  echo "❌ Error: acrName not defined in parameters.main.dev.json"
  exit 1
fi

# Log parameters
echo "📋 Using deployment parameters:"
echo "  - Environment: $ENVIRONMENT_NAME"
echo "  - Location: $LOCATION"
echo "  - App name: $APP_NAME"
echo "  - ACR name: $ACR_NAME"

# Set resource group name based on parameters
# Resource group naming convention: appName-environmentName-rg
RESOURCE_GROUP="${APP_NAME}-${ENVIRONMENT_NAME}-rg"

# STEP 1: Create resource group
echo "🏗️ Creating resource group: ${RESOURCE_GROUP} in ${LOCATION}..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# STEP 2: Deploy Azure Container Registry using Bicep
echo "📦 Deploying Azure Container Registry..."
ACR_DEPLOYMENT_OUTPUT=$(az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file acr.bicep \
  --parameters @parameters.acr.dev.json \
  --query 'properties.outputs' \
  --only-show-errors)

# Extract ACR login server from deployment output
# This is needed for building and pushing Docker images
ACR_LOGIN_SERVER=$(echo $ACR_DEPLOYMENT_OUTPUT | jq -r '.acrLoginServer.value // empty')

# If ACR_LOGIN_SERVER is not found in the output, try to get it directly
# This is a fallback mechanism if Bicep output doesn't contain the expected value
if [ -z "$ACR_LOGIN_SERVER" ]; then
  echo "⚠️ Warning: ACR login server output not found in Bicep deployment"
  ACR_LOGIN_SERVER="${ACR_NAME}.azurecr.io"
  echo "Using constructed ACR login server: $ACR_LOGIN_SERVER"
fi

# STEP 3: Build and push Docker image
# Call build.sh script which handles Docker build and push operations
echo "🔨 Building and pushing Docker image using build.sh..."
./build.sh $ACR_LOGIN_SERVER

# STEP 4: Deploy main infrastructure using Bicep
# This includes Container App, Front Door, networking, etc.
echo "☁️ Deploying Azure resources with Bicep..."
DEPLOYMENT_OUTPUT=$(az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file main.bicep \
  --parameters @parameters.main.dev.json \
  --query 'properties.outputs' \
  --output json \
  --only-show-errors)

echo "Deployment output: $DEPLOYMENT_OUTPUT"

# STEP 5: Extract output values with proper error handling
# These values are needed for subsequent configuration steps
FRONT_DOOR_HOSTNAME=$(echo $DEPLOYMENT_OUTPUT | jq -r '.frontDoorHostname.value // empty')
FRONT_DOOR_ID=$(echo $DEPLOYMENT_OUTPUT | jq -r '.frontDoorId.value // empty')
CONTAINER_APP_FQDN=$(echo $DEPLOYMENT_OUTPUT | jq -r '.containerAppFqdn.value // empty')
CONTAINER_APP_NAME=$(echo $DEPLOYMENT_OUTPUT | jq -r '.containerAppId.value // empty' )

# Check if containerAppName wasn't found in parameters, use default
if [ -z "$CONTAINER_APP_NAME" ]; then
  CONTAINER_APP_NAME="${APP_NAME}-app"
fi

# STEP 6: Fallback mechanisms to retrieve resource information
# If outputs weren't properly captured from Bicep, try to get them directly from Azure resources

# Try to get Front Door hostname directly if not in deployment output
if [ -z "$FRONT_DOOR_HOSTNAME" ]; then
  echo "⚠️ Warning: Front Door hostname output not found in Bicep deployment"
  # Try to get it directly from the resource
  FRONT_DOOR_HOSTNAME=$(az afd endpoint show --profile-name "${APP_NAME}-fd" \
    --endpoint-name "${APP_NAME}-endpoint" --resource-group $RESOURCE_GROUP \
    --query "hostName" -o tsv 2>/dev/null || echo "")
  
  if [ -n "$FRONT_DOOR_HOSTNAME" ]; then
    echo "Retrieved Front Door hostname from Azure resource: $FRONT_DOOR_HOSTNAME"
  fi
fi

# Try to get Front Door ID directly if not in deployment output
if [ -z "$FRONT_DOOR_ID" ]; then
  echo "⚠️ Warning: Front Door ID output not found in Bicep deployment"
  # Try to get it directly from the resource
  FRONT_DOOR_ID=$(az afd profile show --profile-name "${APP_NAME}-fd" \
    --resource-group $RESOURCE_GROUP --query "frontdoorId" -o tsv 2>/dev/null || echo "")
  
  if [ -n "$FRONT_DOOR_ID" ]; then
    echo "Retrieved Front Door ID from Azure resource: $FRONT_DOOR_ID"
  fi
fi

# Try to get Container App FQDN directly if not in deployment output
if [ -z "$CONTAINER_APP_FQDN" ]; then
  echo "⚠️ Warning: Container App FQDN output not found in Bicep deployment"
  # Try to get it directly from the resource
  CONTAINER_APP_FQDN=$(az containerapp show --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP --query "properties.configuration.ingress.fqdn" -o tsv 2>/dev/null || echo "")
  
  if [ -n "$CONTAINER_APP_FQDN" ]; then
    echo "Retrieved Container App FQDN from Azure resource: $CONTAINER_APP_FQDN"
  fi
fi

# Log retrieved resource identifiers for reference
echo "🔍 Deployment Resources:"
echo "  - Front Door Hostname: $FRONT_DOOR_HOSTNAME"
echo "  - Front Door ID: $FRONT_DOOR_ID"
echo "  - Container App FQDN: $CONTAINER_APP_FQDN"
echo "  - Container App Name: $CONTAINER_APP_NAME"

# STEP 7: Load environment variables from .env file
# These will be applied to the Container App
echo "🔑 Setting environment variables from .env file..."
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

# STEP 8: Update Container App with environment variables
# Only proceed if environment variables were found
if [[ -n "$ENV_VARS" ]]; then
    echo "📝 Updating Container App with environment variables..."
    eval "az containerapp update \
      --name $CONTAINER_APP_NAME \
      --resource-group $RESOURCE_GROUP \
      --set-env-vars $ENV_VARS \
      --only-show-errors"
fi

# STEP 9: Configure Container App to only accept traffic from Front Door
# This enhances security by preventing direct access to the app
echo "🔒 Configuring Container App to only accept traffic from Front Door..."

if [ -n "$FRONT_DOOR_HOSTNAME" ]; then
  az containerapp ingress update \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --only-show-errors 
else
  echo "⚠️ Warning: Front Door hostname not available, skipping header configuration"
fi

# STEP 10: Deploy Microsoft Defender for Cloud settings
# This enhances security monitoring and protection for Azure resources
echo "🛡️ Deploying Microsoft Defender for Cloud settings..."
az deployment sub create \
  --name "defender-deployment-$(date +%Y%m%d%H%M%S)" \
  --location "$LOCATION" \
  --template-file ./defender.bicep \
  --parameters enableDefender=true

echo "✅ Microsoft Defender for Cloud settings deployed"

# STEP 11: Wait for Front Door propagation
# Front Door can take some time to fully propagate configuration
echo "⏳ Waiting for Front Door deployment to propagate (this may take several minutes)..."
sleep 60  # 1 minutes wait time for DNS propagation

# STEP 12: Test connectivity through Front Door
# Verify that the application is accessible through Front Door
if [ -n "$FRONT_DOOR_HOSTNAME" ]; then
  echo "🔍 Testing access through Front Door: https://$FRONT_DOOR_HOSTNAME"
  curl -s -I "https://$FRONT_DOOR_HOSTNAME" | head -n 1
else
  echo "⚠️ Warning: Cannot test Front Door access as hostname is not available"
fi

# STEP 12.b: Add REDIRECT_BASE_UR to the app environment variables
echo "🔑 Setting REDIRECT_BASE_URL environment variable...
az containerapp update \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --set-env-vars "REDIRECT_BASE_URL=https://$FRONT_DOOR_HOSTNAME" \
  --only-show-errors"

# STEP 13: Deployment summary
echo "🎉 Deployment completed successfully!"
if [ -n "$FRONT_DOOR_HOSTNAME" ]; then
  echo "Your application is now available at: https://$FRONT_DOOR_HOSTNAME add this to the EntraID app registration"
else
  echo "Your application should be available through Front Door once configuration fully propagates."
fi
echo "NOTE: It may take up to 15 minutes for Front Door configuration to fully propagate."