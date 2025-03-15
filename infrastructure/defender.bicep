targetScope = 'subscription' // Subscription level scope is required

param enableDefender bool = true

// Updated auto provisioning settings 
// Removing deprecated Log Analytics auto provisioning configuration
resource autoProvisioningSettings 'Microsoft.Security/autoProvisioningSettings@2017-08-01-preview' = if (enableDefender) {
  name: 'default'
  properties: {
    // Setting to "Off" since Log Analytics auto provisioning is deprecated
    // Modern Microsoft Defender resources will use Azure Monitor Agent instead
    autoProvision: 'Off'
  }
}

// Microsoft Defender pricing tier resources with latest API version
resource defenderForContainerRegistry 'Microsoft.Security/pricings@2024-01-01' = if (enableDefender) {
  name: 'ContainerRegistry'
  properties: {
    pricingTier: 'Standard'
  }
}

resource defenderForKeyVaults 'Microsoft.Security/pricings@2024-01-01' = if (enableDefender) {
  name: 'KeyVaults'
  properties: {
    pricingTier: 'Standard'
  }
}

resource defenderForStorageAccounts 'Microsoft.Security/pricings@2024-01-01' = if (enableDefender) {
  name: 'StorageAccounts'
  properties: {
    pricingTier: 'Standard'
  }
}

resource defenderForContainers 'Microsoft.Security/pricings@2024-01-01' = if (enableDefender) {
  name: 'Containers'
  properties: {
    pricingTier: 'Standard'
  }
}
