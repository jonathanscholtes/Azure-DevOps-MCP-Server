param appServicePlanName string
@description('Azure region where all resources will be deployed (e.g., "eastus")')
param location string
param webAppName string
param identityName string
param logAnalyticsWorkspaceName string
param appInsightsName string


resource appServicePlan 'Microsoft.Web/serverfarms@2022-03-01' existing = {
  name: appServicePlanName
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' existing = {
  name: appInsightsName
}

resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing= {
  name: identityName
}

resource webApp 'Microsoft.Web/sites@2022-03-01' = {
  name: webAppName
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentity.id}': {}
    }
  }
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      
      linuxFxVersion: 'NODE|20-lts'
      appCommandLine: 'pm2 serve /home/site/wwwroot --spa --no-daemon'
      appSettings: [
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: '0'
        }
          {
            name: 'AZURE_CLIENT_ID'
            value: managedIdentity.properties.clientId
          }
          {
            name: 'AZURE_TENANT_ID'
            value: 'tenantId'
          }
          {
            name: 'MCP_ORGANIZATION'
            value: ''
          }
          {
            name: 'MCP_TRANSPORT'
            value: 'http'
          }
          {
            name: 'MCP_PORT'
            value: '80'
          }
          {
            name: 'MCP_AUTH'
            value: 'external'
          }
      
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: appInsights.properties.InstrumentationKey
        }
      ]
      alwaysOn: true
    }
    publicNetworkAccess: 'Enabled'
    
  }
}

resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2021-06-01'  existing =  {
  name: logAnalyticsWorkspaceName
}

resource diagnosticSettingsAPI 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: '${webAppName}-diagnostic'
  scope: webApp
  properties: {
    workspaceId: logAnalyticsWorkspace.id
    logs: [
      {
        category: 'AppServiceHTTPLogs'
        enabled: true
        retentionPolicy: {
          enabled: false
          days: 0
        }
      }
      {
        category: 'AppServiceConsoleLogs'
        enabled: true
        retentionPolicy: {
          enabled: false
          days: 0
        }
      }
      {
        category: 'AppServiceAppLogs'
        enabled: true
        retentionPolicy: {
          enabled: false
          days: 0
        }
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
        retentionPolicy: {
          enabled: false
          days: 0
        }
      }
    ]
  }
}


output appServiceURL string = 'https://${webAppName}.azurewebsites.net'
output webAppName string = webAppName
