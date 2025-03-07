param location string = 'italynorth'
param appName string = 'ghcp-stats'
param environmentName string = 'prod'

// Container registry parameters
param acrName string = 'ghcpstatsregistry'
param acrSku string = 'Basic'

// Key vault parameters
param keyVaultName string = 'ghcp-stats-kv'

// Storage account parameters
param storageAccountName string = 'ghcpstatsstorage'
param fileShareName string = 'ghcpstatsdata'

// Container app parameters
param containerAppName string = 'ghcp-stats-app'
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
]

// Add these parameters
param frontDoorName string = '${appName}-fd'
param wafPolicyName string = '${appName}-wafpolicy'
param enableDefender bool = true

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
        targetPort: containerPort // Use the containerPort parameter instead of hardcoded 80
        // Add Front Door integration
        ipSecurityRestrictions: [
          {
            name: 'Allow-FrontDoor-Only'
            ipAddressRange: 'AzureFrontDoor.Backend'
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
          name: 'app-client-id' // Add the missing secret
          value: containerAppIdentity.properties.clientId
        }
        {
          name: 'tenant-id' // Add the missing secret
          value: subscription().tenantId
        }
      ]
    }
    template: {
      containers: [
        {
          name: containerAppName // Use the containerAppName parameter
          image: containerImage // Use the containerImage parameter
          env: envVars
          resources: {
            cpu: json('${containerCpu}') // Use the containerCpu parameter
            memory: containerMemory // Use the containerMemory parameter
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

// Add Front Door WAF Policy
resource wafPolicy 'Microsoft.Network/frontdoorwebapplicationfirewallpolicies@2022-05-01' = {
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
    managedRules: {
      managedRuleSets: [
        {
          ruleSetType: 'DefaultRuleSet'
          ruleSetVersion: '1.0'
          ruleGroupOverrides: []
        }
        {
          ruleSetType: 'Microsoft_BotManagerRuleSet'
          ruleSetVersion: '1.0'
          ruleGroupOverrides: []
        }
      ]
    }
  }
}

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
    securityPolicy: {
      id: frontDoorSecurityPolicy.id
    }
  }
}

// Add Front Door Security Policy with WAF
resource frontDoorSecurityPolicy 'Microsoft.Cdn/profiles/securityPolicies@2021-06-01' = {
  parent: frontDoorProfile
  name: '${appName}-security-policy'
  properties: {
    parameters: {
      type: 'WebApplicationFirewall'
      wafPolicy: {
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
}

// Configure Microsoft Defender (Azure Defender)
resource defenderForContainerApps 'Microsoft.Security/pricings@2023-01-01' = if (enableDefender) {
  name: 'ContainerRegistry'
  properties: {
    pricingTier: 'Standard'
  }
}

resource defenderForKeyVault 'Microsoft.Security/pricings@2023-01-01' = if (enableDefender) {
  name: 'KeyVaults'
  properties: {
    pricingTier: 'Standard'
  }
}

resource defenderForStorageAccounts 'Microsoft.Security/pricings@2023-01-01' = if (enableDefender) {
  name: 'StorageAccounts'
  properties: {
    pricingTier: 'Standard'
  }
}

resource defenderForContainers 'Microsoft.Security/pricings@2023-01-01' = if (enableDefender) {
  name: 'Containers'
  properties: {
    pricingTier: 'Standard'
  }
}

// Add auto-provisioning of the monitoring agent
resource autoProvisioningSettings 'Microsoft.Security/autoProvisioningSettings@2017-08-01-preview' = if (enableDefender) {
  name: 'default'
  properties: {
    autoProvision: 'On'
  }
}

// Add outputs for the Front Door endpoint
output frontDoorEndpointUrl string = 'https://${frontDoorEndpoint.properties.hostName}'
output containerAppDirectUrl string = 'https://${containerApp.properties.configuration.ingress.fqdn}'
