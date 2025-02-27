#!/bin/bash

# Set variables
RESOURCE_GROUP="ghcp-stats-rg"
LOCATION="italynorth"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Deploy Bicep template
az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file main.bicep \
  --parameters environmentName=prod