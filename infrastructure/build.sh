#!/bin/bash

# Build script for GHCP-Stats v2 (using uv package manager)
# This script builds a Docker image that uses uv for dependency management

# Read parameters from parameters.prod.json
ENVIRONMENT_NAME=$(jq -r '.parameters.environmentName.value' parameters.main.dev.json)
LOCATION=$(jq -r '.parameters.location.value' parameters.main.dev.json)
APP_NAME=$(jq -r '.parameters.appName.value' parameters.main.dev.json)
ACR_NAME=$(jq -r '.parameters.acrName.value' parameters.main.dev.json)

# Authenticate with ACR
az acr login --name $ACR_NAME

# Build and push Docker image with platform specified as linux/amd64
cd ../app  # Navigate to app directory relative to infrastructure folder

# Ensure uv.lock file is up to date
echo "📦 Updating uv.lock file..."
uv lock
docker buildx create --use --name multiarch --driver docker-container
docker buildx build --platform linux/amd64 -t ghcp-stats:latest --load .

ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer --output tsv)
docker tag ghcp-stats:latest $ACR_LOGIN_SERVER/ghcp-stats:latest
docker push $ACR_LOGIN_SERVER/ghcp-stats:latest