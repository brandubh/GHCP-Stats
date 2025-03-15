param location string = 'italynorth'
param appName string = 'ghcp-stats'
param environmentName string = 'dev'

// Container registry parameters
param acrName string = 'ghcpstatsregistry'
param acrSku string = 'Basic'

// Key vault parameters
param keyVaultName string = 'ghcp-stats-kv-${environmentName}'

// Storage account parameters
param storageAccountName string = 'ghcpstatsstorage'
param fileShareName string = 'ghcpstatsdata${environmentName}'

// Container app parameters
param containerAppName string = 'ghcp-stats-app-${environmentName}'
param containerImage string = '${acrName}.azurecr.io/ghcp-stats:latest'
param containerPort int = 8501
param containerCpu string = '0.5'
param containerMemory string = '1Gi'

param envVars array = [
  {
    name: 'KEY_VAULT_NAME'
    value: keyVaultName
  }
  {
    name: 'DB_NAME'
    value: '/app/data/metrics.db'
  }
  {
    name: 'AZURE_CLIENT_ID'
    secretRef: 'app-client-id'
  }
]

// Add these parameters
param frontDoorName string = '${appName}-fd'
param wafPolicyName string = '${appName}wafpolicy'
param frontDoorIpRanges array = [
  '4.213.28.114/31'
  '4.213.81.64/29'
  '4.232.98.120/29'
  '13.73.248.16/29'
  '20.17.126.64/29'
  '20.21.37.40/29'
  '20.36.120.104/29'
  '20.37.64.104/29'
  '20.37.156.120/29'
  '20.37.195.0/29'
  '20.37.224.104/29'
  '20.38.84.72/29'
  '20.38.136.104/29'
  '20.39.11.8/29'
  '20.41.4.88/29'
  '20.41.64.120/29'
  '20.41.192.104/29'
  '20.42.4.120/29'
  '20.42.129.152/29'
  '20.42.224.104/29'
  '20.43.41.136/29'
  '20.43.65.128/29'
  '20.43.130.80/29'
  '20.45.112.104/29'
  '20.45.192.104/29'
  '20.59.103.64/29'
  '20.72.18.248/29'
  '20.79.107.152/29'
  '20.88.157.176/29'
  '20.90.132.152/29'
  '20.113.254.88/29'
  '20.115.247.64/29'
  '20.118.195.128/29'
  '20.119.155.128/29'
  '20.150.160.96/29'
  '20.189.106.112/29'
  '20.192.161.104/29'
  '20.192.225.48/29'
  '20.210.70.64/30'
  '20.215.4.240/29'
  '20.217.44.240/29'
  '40.67.48.104/29'
  '40.74.30.72/29'
  '40.80.56.104/29'
  '40.80.168.104/29'
  '40.80.184.120/29'
  '40.82.248.248/29'
  '40.89.16.104/29'
  '51.12.41.8/29'
  '51.12.193.8/29'
  '51.53.30.144/29'
  '51.104.25.128/29'
  '51.105.80.104/29'
  '51.105.88.104/29'
  '51.107.48.104/29'
  '51.107.144.104/29'
  '51.120.40.104/29'
  '51.120.224.104/29'
  '51.137.160.112/29'
  '51.143.192.104/29'
  '52.136.48.104/29'
  '52.140.104.104/29'
  '52.150.136.120/29'
  '52.159.71.160/29'
  '52.228.80.120/29'
  '68.210.172.176/29'
  '68.221.93.128/29'
  '69.15.0.0/16'
  '102.133.56.88/29'
  '102.133.216.88/29'
  '147.243.0.0/16'
  '157.55.93.2/31'
  '158.23.108.56/29'
  '172.204.165.112/29'
  '172.207.68.70/31'
  '172.207.69.80/30'
  '191.233.9.120/29'
  '191.235.225.128/29'
]

// Log Analytics for Container Apps Environment
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: '${appName}-logs'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// Create managed identity for Container App
resource containerAppIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: '${containerAppName}-identity'
  location: location
}

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
    accessPolicies: [
      {
        tenantId: subscription().tenantId
        objectId: containerAppIdentity.properties.principalId
        permissions: {
          secrets: ['get', 'list']
        }
      }
    ]
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

// Create File Share - fix: use parent property
resource fileServices 'Microsoft.Storage/storageAccounts/fileServices@2023-01-01' = {
  parent: storageAccount
  name: 'default'
}

resource fileShare 'Microsoft.Storage/storageAccounts/fileServices/shares@2023-01-01' = {
  parent: fileServices
  name: fileShareName
}

// Correct version with proper schema properties
resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: '${appName}-env'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsWorkspace.properties.customerId
        sharedKey: logAnalyticsWorkspace.listKeys().primarySharedKey
      }
    }
  }
}

// Create Azure File Share storage resource in the Container Apps Environment
resource fileShareStorage 'Microsoft.App/managedEnvironments/storages@2023-05-01' = {
  name: fileShareName
  parent: containerAppsEnvironment
  properties: {
    azureFile: {
      accountName: storageAccount.name
      accountKey: storageAccount.listKeys().keys[0].value
      shareName: fileShareName
      accessMode: 'ReadWrite'
    }
  }
}

// Container App that uses the Azure File storage
resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: containerAppName
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${containerAppIdentity.id}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      ingress: {
        external: true
        targetPort: containerPort
        allowInsecure: false
        traffic: [
          {
            weight: 100
            latestRevision: true
          }
        ]
        // Use access restrictions correctly for Front Door

        ipSecurityRestrictions: [
          for ipRange in frontDoorIpRanges: {
            name: 'AllowAzureFrontDoor_${replace(ipRange, '/', '_')}'
            description: 'Allow traffic from Azure Front Door IP range ${ipRange}'
            ipAddressRange: ipRange
            action: 'Allow'
          }
        ]
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
        {
          name: 'app-client-id'
          value: containerAppIdentity.properties.clientId
        }
        {
          name: 'tenant-id'
          value: subscription().tenantId
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
            cpu: json('${containerCpu}')
            memory: containerMemory
          }
          volumeMounts: [
            {
              volumeName: 'azure-files-volume'
              mountPath: '/app/data'
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
          name: 'azure-files-volume'
          storageType: 'AzureFile'
          storageName: fileShareName
        }
      ]
    }
  }
}

// Add Front Door WAF Policy - FIXED
resource wafPolicy 'Microsoft.Network/frontdoorwebapplicationfirewallpolicies@2024-02-01' = {
  name: wafPolicyName
  location: 'global'
  sku: {
    name: 'Standard_AzureFrontDoor'
  }
  properties: {
    policySettings: {
      enabledState: 'Enabled'
      mode: 'Prevention'
    }
  }
}

output wafPolicyId string = wafPolicy.id

// Add Azure Front Door Profile
resource frontDoorProfile 'Microsoft.Cdn/profiles@2021-06-01' = {
  name: frontDoorName
  location: 'global'
  sku: {
    name: 'Standard_AzureFrontDoor'
  }
}

// Add Front Door Endpoint
resource frontDoorEndpoint 'Microsoft.Cdn/profiles/afdEndpoints@2021-06-01' = {
  parent: frontDoorProfile
  name: '${appName}-endpoint'
  location: 'global'
  properties: {
    enabledState: 'Enabled'
  }
}

// Add Front Door Origin Group
resource frontDoorOriginGroup 'Microsoft.Cdn/profiles/originGroups@2021-06-01' = {
  parent: frontDoorProfile
  name: '${appName}-origin-group'
  properties: {
    loadBalancingSettings: {
      sampleSize: 4
      successfulSamplesRequired: 3
      additionalLatencyInMilliseconds: 50
    }
    healthProbeSettings: {
      probePath: '/'
      probeRequestType: 'GET'
      probeProtocol: 'Https'
      probeIntervalInSeconds: 100
    }
  }
}

// Add Front Door Origin (pointing to Container App)
resource frontDoorOrigin 'Microsoft.Cdn/profiles/originGroups/origins@2021-06-01' = {
  parent: frontDoorOriginGroup
  name: '${appName}-origin'
  properties: {
    hostName: containerApp.properties.configuration.ingress.fqdn
    httpPort: 80
    httpsPort: 443
    originHostHeader: containerApp.properties.configuration.ingress.fqdn
    priority: 1
    weight: 1000
    enabledState: 'Enabled'
  }
}

// Add Front Door Route
resource frontDoorRoute 'Microsoft.Cdn/profiles/afdEndpoints/routes@2021-06-01' = {
  parent: frontDoorEndpoint
  name: '${appName}-route'
  properties: {
    originGroup: {
      id: frontDoorOriginGroup.id
    }
    supportedProtocols: [
      'Http'
      'Https'
    ]
    patternsToMatch: [
      '/*'
    ]
    forwardingProtocol: 'HttpsOnly'
    linkToDefaultDomain: 'Enabled'
    httpsRedirect: 'Enabled'
    enabledState: 'Enabled'
    // Remove this reference to avoid circular dependency
    // securityPolicy: {
    //   id: frontDoorSecurityPolicy.id
    // }
  }
}

// Add Front Door Security Policy with WAF
resource frontDoorSecurityPolicy 'Microsoft.Cdn/profiles/securityPolicies@2024-02-01' = {
  parent: frontDoorProfile
  name: '${appName}-security-policy'
  properties: {
    parameters: {
      type: 'WebApplicationFirewall'
      wafPolicy: {
        // Use subscription and resource group in the resource ID for complete path
        id: wafPolicy.id
      }
      associations: [
        {
          domains: [
            {
              id: frontDoorEndpoint.id
            }
          ]
          patternsToMatch: [
            '/*'
          ]
        }
      ]
    }
  }
  // Add explicit dependency to ensure WAF policy exists first
  dependsOn: [
    wafPolicy
  ]
}

// Add output values for deploy.sh
output containerAppFqdn string = containerApp.properties.configuration.ingress.fqdn
output frontDoorHostname string = frontDoorEndpoint.properties.hostName
output frontDoorId string = frontDoorProfile.properties.frontDoorId
output containerAppId string = containerApp.name
