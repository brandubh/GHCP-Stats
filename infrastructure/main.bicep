param location string = 'italynorth'
param appName string = 'ghcp-stats'
param environmentName string = 'prod'

// Container registry parameters
param acrName string = 'ghcpstatsregistry${uniqueString(resourceGroup().id)}'
param acrSku string = 'Basic'

// Key vault parameters
param keyVaultName string = 'ghcp-stats-kv${uniqueString(resourceGroup().id)}'

// Storage account parameters
param storageAccountName string = 'ghcpstats${uniqueString(resourceGroup().id)}'
param fileShareName string = 'ghcpstatsdata'

// Container app parameters
param containerAppName string = 'ghcp-stats-app'
param containerImage string = '${acrName}.azurecr.io/ghcp-stats:latest'
param containerPort int = 8501
param envVars array = [
  {
    name: 'AZURE_CLIENT_ID'
    secretRef: 'app-client-id'
  }
  {
    name: 'AZURE_TENANT_ID'
    secretRef: 'tenant-id'
  }
  {
    name: 'KEY_VAULT_NAME'
    value: keyVaultName
  }
  {
    name: 'DB_NAME'
    value: '/app/data/metrics.db'
  }
]

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

// Create Key Vault
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    enabledForDeployment: true
    enabledForTemplateDeployment: true
    enabledForDiskEncryption: true
    tenantId: subscription().tenantId
    accessPolicies: []
    sku: {
      name: 'standard'
      family: 'A'
    }
  }
}

// Create Storage Account
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    supportsHttpsTrafficOnly: true
    encryption: {
      services: {
        file: {
          keyType: 'Account'
          enabled: true
        }
      }
      keySource: 'Microsoft.Storage'
    }
  }
}

// Create File Share
resource fileShare 'Microsoft.Storage/storageAccounts/fileServices/shares@2023-01-01' = {
  name: '${storageAccount.name}/default/${fileShareName}'
}

// Create Container Apps Environment
resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: '${appName}-${environmentName}-env'
  location: location
  properties: {
    zoneRedundant: false
  }
}

// Create Container App
resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: containerAppName
  location: location
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      ingress: {
        external: true
        targetPort: containerPort
      }
      registries: [
        {
          server: '${acrName}.azurecr.io'
          username: acr.listCredentials().username
          passwordSecretRef: 'registry-password'
        }
      ]
      secrets: [
        {
          name: 'registry-password'
          value: acr.listCredentials().passwords[0].value
        }
      ]
    }
    template: {
      containers: [
        {
          name: containerAppName
          image: containerImage
          env: envVars
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          volumeMounts: [
            {
              mountPath: '/app/data'
              volumeName: 'data-volume'
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 1
      }
      volumes: [
        {
          name: 'data-volume'
          storageType: 'AzureFile'
          storageName: fileShare.name
        }
      ]
    }
  }
}

// Output values
output acrLoginServer string = acr.properties.loginServer
output keyVaultUri string = keyVault.properties.vaultUri
output containerAppFqdn string = containerApp.properties.configuration.ingress.fqdn
