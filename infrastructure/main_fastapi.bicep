param location string = resourceGroup().location
param cosmosAccountName string
param containerAppName string
param containerImage string

resource cosmos 'Microsoft.DocumentDB/databaseAccounts@2023-04-15' = {
  name: cosmosAccountName
  location: location
  kind: 'MongoDB'
  properties: {
    databaseAccountOfferType: 'Standard'
  }
}

resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: containerAppName
  location: location
  properties: {
    kubeEnvironmentId: '/subscriptions/.../resourceGroups/.../providers/Microsoft.App/managedEnvironments/...'
    configuration: {
      ingress: { external: true, targetPort: 8000 }
    }
    template: {
      containers: [
        {
          name: 'ghcpstats'
          image: containerImage
        }
      ]
    }
  }
}
