// ============================================================================
// ZavaCloud Helpdesk Demo Infrastructure - Main Entry Point (azd)
// Azure AI Foundry + Azure AI Search + APIM + Logic Apps
// ============================================================================

targetScope = 'subscription'

// ============================================================================
// Parameters
// ============================================================================

@minLength(1)
@maxLength(64)
@description('Name of the environment (maps to azd AZURE_ENV_NAME)')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Location override for Azure API Management (allows deploying APIM to a different region than other resources). Defaults to the primary location.')
param apimLocation string = ''

@description('Principal ID to grant access to resources')
param principalId string = ''

@description('AI Search SKU')
@allowed(['basic', 'standard', 'standard2', 'standard3'])
param aiSearchSku string = 'basic'

@description('The name of the model to deploy')
param modelName string = 'gpt-5.4'

@description('The model format/provider')
param modelFormat string = 'OpenAI'

@description('The model version')
param modelVersion string = '2026-03-05'

@description('The model SKU name')
param modelSkuName string = 'GlobalStandard'

@description('The model capacity (TPM in thousands)')
param modelCapacity int = 30

@description('Salesforce environment - production or sandbox')
@allowed(['production', 'sandbox'])
param salesforceEnvironment string = 'production'

@secure()
@description('Salesforce OAuth Client ID (from SFDC_CLIENT_ID)')
param salesforceClientId string = ''

@secure()
@description('Salesforce OAuth Client Secret (from SFDC_CLIENT_SECRET)')
param salesforceClientSecret string = ''

@description('Salesforce OAuth Token Endpoint')
param salesforceTokenEndpoint string = 'https://login.salesforce.com/services/oauth2/token'

// ============================================================================
// Variables
// ============================================================================

var abbrs = loadJsonContent('./abbreviations.json')
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var tags = {
  'azd-env-name': environmentName
  project: 'zava-helpdesk-demo'
}

// ============================================================================
// Resource Group
// ============================================================================

resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: '${abbrs.resourceGroup}${environmentName}'
  location: location
  tags: tags
}

// ============================================================================
// Resources Module
// ============================================================================

module resources 'resources.bicep' = {
  name: 'resources'
  scope: rg
  params: {
    location: location
    tags: tags
    resourceToken: resourceToken
    principalId: principalId
    aiSearchSku: aiSearchSku
    modelName: modelName
    modelFormat: modelFormat
    modelVersion: modelVersion
    modelSkuName: modelSkuName
    modelCapacity: modelCapacity
    salesforceEnvironment: salesforceEnvironment
  }
}

// ============================================================================
// APIM Module
// ============================================================================

module apim 'apim.bicep' = {
  name: 'apim'
  scope: rg
  params: {
    environmentName: environmentName
    location: empty(apimLocation) ? location : apimLocation
    principalId: principalId
    salesforceClientId: salesforceClientId
    salesforceClientSecret: salesforceClientSecret
    salesforceTokenEndpoint: salesforceTokenEndpoint
    logAnalyticsWorkspaceId: resources.outputs.logAnalyticsWorkspaceId
  }
}

// ============================================================================
// Outputs (azd reads these automatically)
// ============================================================================

// Resource Group
output AZURE_RESOURCE_GROUP string = rg.name

// AI Foundry
output AZURE_AI_FOUNDRY_NAME string = resources.outputs.aiFoundryName
output AZURE_AI_FOUNDRY_ENDPOINT string = resources.outputs.aiFoundryEndpoint
output AZURE_OPENAI_ENDPOINT string = resources.outputs.aiOpenAIEndpoint
output AZURE_AI_PROJECT_NAME string = resources.outputs.aiProjectName
output AZURE_AI_PROJECT_ENDPOINT string = resources.outputs.aiProjectEndpoint
output AZURE_AI_PROJECT_CONNECTION_STRING string = resources.outputs.aiProjectConnectionString

// AI Search
output AZURE_SEARCH_NAME string = resources.outputs.aiSearchName
output AZURE_SEARCH_ENDPOINT string = resources.outputs.aiSearchEndpoint
output AZURE_SEARCH_INDEX string = 'helpdesk-knowledge'

// Application Insights
output APPLICATIONINSIGHTS_NAME string = resources.outputs.appInsightsName
output APPLICATIONINSIGHTS_CONNECTION_STRING string = resources.outputs.appInsightsConnectionString

// Model
output AZURE_OPENAI_DEPLOYMENT string = resources.outputs.modelDeploymentName

// Logic App (Salesforce Integration)
output LOGIC_APP_NAME string = resources.outputs.logicAppName
output LOGIC_APP_ID string = resources.outputs.logicAppId
output SALESFORCE_CONNECTION_NAME string = resources.outputs.salesforceConnectionName
output SALESFORCE_CONNECTION_ID string = resources.outputs.salesforceConnectionId

// APIM
output APIM_ENDPOINT string = apim.outputs.apimEndpoint
output APIM_MCP_SERVER_PATH string = apim.outputs.apimMcpServerPath
output APIM_NAME string = apim.outputs.apimName
output APIM_SUBSCRIPTION_ID string = apim.outputs.subscriptionId
