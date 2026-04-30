// SynthData — Azure Infrastructure (Bicep)
// Deploys: Container Apps Environment, Container App, Azure OpenAI, Speech, Blob Storage, Key Vault

targetScope = 'resourceGroup'

@description('Primary location for all resources')
param location string = resourceGroup().location

@description('Environment name (dev, staging, prod)')
param environmentName string = 'dev'

@description('Container image tag')
param imageTag string = 'latest'

var prefix = 'synthdata-${environmentName}'

// --- Log Analytics Workspace ---
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${prefix}-logs'
  location: location
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: 30
  }
}

// --- Container Apps Environment ---
resource containerEnv 'Microsoft.App/managedEnvironments@2023-11-02-preview' = {
  name: '${prefix}-env'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
  }
}

// --- Storage Account ---
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: replace('${prefix}store', '-', '')
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
  }
}

// --- Key Vault ---
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: '${prefix}-kv'
  location: location
  properties: {
    tenantId: subscription().tenantId
    sku: { family: 'A', name: 'standard' }
    enableRbacAuthorization: true
    enableSoftDelete: true
  }
}

// --- Container App (Backend API) ---
resource containerApp 'Microsoft.App/containerApps@2023-11-02-preview' = {
  name: '${prefix}-api'
  location: location
  properties: {
    managedEnvironmentId: containerEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        transport: 'http'
      }
    }
    template: {
      containers: [
        {
          name: 'synthdata-api'
          image: 'ghcr.io/fratei/synthdata-app:${imageTag}'
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            { name: 'APP_NAME', value: 'SynthData' }
            { name: 'PORT', value: '8000' }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 10
        rules: [
          {
            name: 'http-scaling'
            http: { metadata: { concurrentRequests: '50' } }
          }
        ]
      }
    }
  }
}

output apiUrl string = 'https://${containerApp.properties.configuration.ingress.fqdn}'
output storageAccountName string = storageAccount.name
output keyVaultName string = keyVault.name
