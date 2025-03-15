param location string = 'italynorth'
param environment string = 'dev'
// Container registry parameters
param acrName string = 'ghcpstatsregistry'
param acrSku string = 'Basic'

// Create Azure Container Registry
resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: acrName
  location: location
  sku: {
    name: acrSku
  }
  properties: {
    adminUserEnabled: true
  }
}
