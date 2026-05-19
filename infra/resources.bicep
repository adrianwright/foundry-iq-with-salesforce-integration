// ============================================================================
// ZavaCloud Helpdesk Demo - Resources Module
// All Azure resources deployed to the resource group
// ============================================================================

@description('Location for all resources')
param location string

@description('Tags to apply to all resources')
param tags object

@description('Unique token for resource naming')
param resourceToken string

@description('Principal ID for role assignments')
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

// ============================================================================
// Variables
// ============================================================================

var abbrs = loadJsonContent('./abbreviations.json')
var aiFoundryName = '${abbrs.cognitiveServices}${resourceToken}'
var aiProjectName = 'project-${resourceToken}'
var aiSearchName = '${abbrs.searchService}${resourceToken}'
var logAnalyticsName = '${abbrs.logAnalytics}${resourceToken}'
var storageAccountName = '${abbrs.storageAccount}${resourceToken}'
var logicAppName = '${abbrs.logicApp}salesforce-${resourceToken}'
var logicAppUpdateName = '${abbrs.logicApp}sf-update-${resourceToken}'
var salesforceConnectionName = 'salesforce-connection-${resourceToken}'
var salesforceLoginUri = salesforceEnvironment == 'production' ? 'https://login.salesforce.com' : 'https://test.salesforce.com'

// ============================================================================
// Log Analytics Workspace
// ============================================================================

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: logAnalyticsName
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// ============================================================================
// Application Insights
// ============================================================================

var appInsightsName = '${abbrs.appInsights}${resourceToken}'

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
    IngestionMode: 'LogAnalytics'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

// ============================================================================
// Storage Account (for AI Foundry)
// ============================================================================

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageAccountName
  location: location
  tags: tags
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    supportsHttpsTrafficOnly: true
    accessTier: 'Hot'
  }
}

// ============================================================================
// Azure AI Foundry (Cognitive Services Account)
// ============================================================================

resource aiFoundry 'Microsoft.CognitiveServices/accounts@2025-04-01-preview' = {
  name: aiFoundryName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  sku: {
    name: 'S0'
  }
  kind: 'AIServices'
  properties: {
    allowProjectManagement: true
    customSubDomainName: aiFoundryName
    disableLocalAuth: false
    publicNetworkAccess: 'Enabled'
  }
}

// ============================================================================
// AI Foundry Project
// ============================================================================

resource aiProject 'Microsoft.CognitiveServices/accounts/projects@2025-04-01-preview' = {
  parent: aiFoundry
  name: aiProjectName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    description: 'ZavaCloud Helpdesk RAG Chatbot Demo'
    displayName: 'Helpdesk Chatbot'
  }
}

// ============================================================================
// Model Deployment (GPT-5.4) — used for both the agent and the Foundry IQ KB
// ============================================================================

resource modelDeployment 'Microsoft.CognitiveServices/accounts/deployments@2025-04-01-preview' = {
  parent: aiFoundry
  name: modelName
  sku: {
    name: modelSkuName
    capacity: modelCapacity
  }
  properties: {
    model: {
      format: modelFormat
      name: modelName
      version: modelVersion
    }
  }
}

// ============================================================================
// Model Deployment (text-embedding-3-small)
// ============================================================================

resource embeddingDeployment 'Microsoft.CognitiveServices/accounts/deployments@2025-04-01-preview' = {
  parent: aiFoundry
  name: 'text-embedding-3-small'
  dependsOn: [modelDeployment]
  sku: {
    name: 'GlobalStandard'
    capacity: 100
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'text-embedding-3-small'
      version: '1'
    }
  }
}

// ============================================================================
// Azure AI Search
// ============================================================================

resource aiSearch 'Microsoft.Search/searchServices@2024-06-01-preview' = {
  name: aiSearchName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  sku: {
    name: aiSearchSku
  }
  properties: {
    replicaCount: 1
    partitionCount: 1
    hostingMode: 'default'
    publicNetworkAccess: 'enabled'
    authOptions: {
      aadOrApiKey: {
        aadAuthFailureMode: 'http401WithBearerChallenge'
      }
    }
    semanticSearch: 'free'
  }
}

// ============================================================================
// Application Insights Connection for Foundry Tracing
// ============================================================================

resource appInsightsConnection 'Microsoft.CognitiveServices/accounts/connections@2025-04-01-preview' = {
  parent: aiFoundry
  name: 'appinsights-connection'
  properties: {
    category: 'AppInsights'
    target: appInsights.id
    authType: 'ApiKey'
    isSharedToAll: true
    credentials: {
      key: appInsights.properties.ConnectionString
    }
    metadata: {
      ApiType: 'Azure'
      ResourceId: appInsights.id
    }
  }
}

// ============================================================================
// Role Assignments
// ============================================================================

// Project MI -> Search Index Data Reader (required for Foundry IQ KB/MCP access)
resource projectSearchReaderRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: aiSearch
  name: guid(aiSearch.id, aiProject.id, '1407120a-92aa-4202-b7e9-c0e197c71c8f')
  properties: {
    principalId: aiProject.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '1407120a-92aa-4202-b7e9-c0e197c71c8f') // Search Index Data Reader
    principalType: 'ServicePrincipal'
  }
}

// AI Foundry MI -> Search Index Data Contributor (for index management)
resource foundrySearchContributorRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: aiSearch
  name: guid(aiSearch.id, aiFoundry.id, '8ebe5a00-799e-43f5-93ac-243d3dce84a7')
  properties: {
    principalId: aiFoundry.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '8ebe5a00-799e-43f5-93ac-243d3dce84a7') // Search Index Data Contributor
    principalType: 'ServicePrincipal'
  }
}

// Search MI -> AOAI: Cognitive Services OpenAI User
// Required so the Search service can call AOAI chat/completions for the Foundry
// knowledge base's model query planning + semantic ranking inside knowledge_base_retrieve.
// This is the ONLY role required for AAD inference; "Cognitive Services User" and
// "Azure AI Developer" are NOT needed for the data action
// Microsoft.CognitiveServices/accounts/OpenAI/deployments/chat/completions/action.
resource searchAoaiOpenAIUserRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: aiFoundry
  name: guid(aiFoundry.id, aiSearch.id, '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd')
  properties: {
    principalId: aiSearch.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd') // Cognitive Services OpenAI User
    principalType: 'ServicePrincipal'
  }
}

// ============================================================================
// Logic App with Salesforce Trigger
// ============================================================================

// Salesforce API Connection
resource salesforceConnection 'Microsoft.Web/connections@2016-06-01' = {
  name: salesforceConnectionName
  location: location
  tags: tags
  properties: {
    displayName: 'Salesforce Connection'
    api: {
      id: subscriptionResourceId('Microsoft.Web/locations/managedApis', location, 'salesforce')
    }
    parameterValues: {
      'token:LoginUri': salesforceLoginUri
    }
  }
}

// Logic App Workflow
resource logicApp 'Microsoft.Logic/workflows@2019-05-01' = {
  name: logicAppName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    state: 'Enabled'
    definition: {
      '$schema': 'https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#'
      contentVersion: '1.0.0.0'
      parameters: {
        '$connections': {
          defaultValue: {}
          type: 'Object'
        }
        openai_endpoint: {
          defaultValue: 'https://${aiFoundry.name}.cognitiveservices.azure.com'
          type: 'String'
        }
        search_endpoint: {
          defaultValue: 'https://${aiSearch.name}.search.windows.net'
          type: 'String'
        }
        search_index: {
          defaultValue: 'service-cases'
          type: 'String'
        }
      }
      triggers: {
        When_a_record_is_created: {
          type: 'ApiConnection'
          inputs: {
            host: {
              connection: {
                name: '@parameters(\'$connections\')[\'salesforce\'][\'connectionId\']'
              }
            }
            method: 'get'
            path: '/datasets/default/tables/@{encodeURIComponent(encodeURIComponent(\'Case\'))}/onnewitems'
          }
          recurrence: {
            interval: 30
            frequency: 'Second'
          }
          splitOn: '@triggerBody()?[\'value\']'
        }
      }
      actions: {
        Initialize_content: {
          type: 'InitializeVariable'
          inputs: {
            variables: [
              {
                name: 'content'
                type: 'string'
                value: '@{coalesce(triggerBody()?[\'Subject\'], \'\')} @{coalesce(triggerBody()?[\'Description\'], \'\')} @{coalesce(triggerBody()?[\'Resolution\'], \'\')}'
              }
            ]
          }
          runAfter: {}
        }
        Generate_Embeddings: {
          type: 'Http'
          inputs: {
            method: 'POST'
            uri: '@{parameters(\'openai_endpoint\')}/openai/deployments/text-embedding-3-small/embeddings?api-version=2024-06-01'
            headers: {
              'Content-Type': 'application/json'
            }
            body: {
              input: '@variables(\'content\')'
            }
            authentication: {
              type: 'ManagedServiceIdentity'
              audience: 'https://cognitiveservices.azure.com'
            }
          }
          runAfter: {
            Initialize_content: ['Succeeded']
          }
        }
        Index_to_Search: {
          type: 'Http'
          inputs: {
            method: 'POST'
            uri: '@{parameters(\'search_endpoint\')}/indexes/@{parameters(\'search_index\')}/docs/index?api-version=2024-07-01'
            headers: {
              'Content-Type': 'application/json'
            }
            body: {
              value: [
                {
                  '@@search.action': 'upload'
                  id: '@{triggerBody()?[\'Id\']}'
                  case_number: '@{triggerBody()?[\'CaseNumber\']}'
                  subject: '@{coalesce(triggerBody()?[\'Subject\'], \'\')}'
                  description: '@{coalesce(triggerBody()?[\'Description\'], \'\')}'
                  content_vector: '@body(\'Generate_Embeddings\')?[\'data\']?[0]?[\'embedding\']'
                  status: '@{coalesce(triggerBody()?[\'Status\'], \'\')}'
                  priority: '@{coalesce(triggerBody()?[\'Priority\'], \'\')}'
                  origin: '@{coalesce(triggerBody()?[\'Origin\'], \'\')}'
                  case_type: '@{coalesce(triggerBody()?[\'Type\'], \'\')}'
                  contact_email: '@{coalesce(triggerBody()?[\'ContactEmail\'], \'\')}'
                  account_name: '@{coalesce(triggerBody()?[\'Account\']?[\'Name\'], \'\')}'
                  resolution: '@{coalesce(triggerBody()?[\'Resolution\'], \'\')}'
                  owner_name: '@{coalesce(triggerBody()?[\'Owner\']?[\'Name\'], \'\')}'
                  salesforce_id: '@{triggerBody()?[\'Id\']}'
                }
              ]
            }
            authentication: {
              type: 'ManagedServiceIdentity'
              audience: 'https://search.azure.com'
            }
          }
          runAfter: {
            Generate_Embeddings: ['Succeeded']
          }
        }
      }
    }
    parameters: {
      '$connections': {
        value: {
          salesforce: {
            connectionId: salesforceConnection.id
            connectionName: salesforceConnection.name
            id: subscriptionResourceId('Microsoft.Web/locations/managedApis', location, 'salesforce')
          }
        }
      }
    }
  }
}

// Logic App (Update) Workflow
resource logicAppUpdate 'Microsoft.Logic/workflows@2019-05-01' = {
  name: logicAppUpdateName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    state: 'Enabled'
    definition: {
      '$schema': 'https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#'
      contentVersion: '1.0.0.0'
      parameters: {
        '$connections': {
          defaultValue: {}
          type: 'Object'
        }
        openai_endpoint: {
          defaultValue: 'https://${aiFoundry.name}.cognitiveservices.azure.com'
          type: 'String'
        }
        search_endpoint: {
          defaultValue: 'https://${aiSearch.name}.search.windows.net'
          type: 'String'
        }
        search_index: {
          defaultValue: 'service-cases'
          type: 'String'
        }
      }
      triggers: {
        When_a_record_is_modified: {
          type: 'ApiConnection'
          inputs: {
            host: {
              connection: {
                name: '@parameters(\'$connections\')[\'salesforce\'][\'connectionId\']'
              }
            }
            method: 'get'
            path: '/datasets/default/tables/@{encodeURIComponent(encodeURIComponent(\'Case\'))}/onupdateditems'
          }
          recurrence: {
            interval: 30
            frequency: 'Second'
          }
          splitOn: '@triggerBody()?[\'value\']'
        }
      }
      actions: {
        Initialize_content: {
          type: 'InitializeVariable'
          inputs: {
            variables: [
              {
                name: 'content'
                type: 'string'
                value: '@{coalesce(triggerBody()?[\'Subject\'], \'\')} @{coalesce(triggerBody()?[\'Description\'], \'\')} @{coalesce(triggerBody()?[\'Resolution\'], \'\')}'
              }
            ]
          }
          runAfter: {}
        }
        Generate_Embeddings: {
          type: 'Http'
          inputs: {
            method: 'POST'
            uri: '@{parameters(\'openai_endpoint\')}/openai/deployments/text-embedding-3-small/embeddings?api-version=2024-06-01'
            headers: {
              'Content-Type': 'application/json'
            }
            body: {
              input: '@variables(\'content\')'
            }
            authentication: {
              type: 'ManagedServiceIdentity'
              audience: 'https://cognitiveservices.azure.com'
            }
          }
          runAfter: {
            Initialize_content: ['Succeeded']
          }
        }
        Index_to_Search: {
          type: 'Http'
          inputs: {
            method: 'POST'
            uri: '@{parameters(\'search_endpoint\')}/indexes/@{parameters(\'search_index\')}/docs/index?api-version=2024-07-01'
            headers: {
              'Content-Type': 'application/json'
            }
            body: {
              value: [
                {
                  '@@search.action': 'merge'
                  id: '@{triggerBody()?[\'Id\']}'
                  case_number: '@{triggerBody()?[\'CaseNumber\']}'
                  subject: '@{coalesce(triggerBody()?[\'Subject\'], \'\')}'
                  description: '@{coalesce(triggerBody()?[\'Description\'], \'\')}'
                  content_vector: '@body(\'Generate_Embeddings\')?[\'data\']?[0]?[\'embedding\']'
                  status: '@{coalesce(triggerBody()?[\'Status\'], \'\')}'
                  priority: '@{coalesce(triggerBody()?[\'Priority\'], \'\')}'
                  origin: '@{coalesce(triggerBody()?[\'Origin\'], \'\')}'
                  case_type: '@{coalesce(triggerBody()?[\'Type\'], \'\')}'
                  contact_email: '@{coalesce(triggerBody()?[\'ContactEmail\'], \'\')}'
                  account_name: '@{coalesce(triggerBody()?[\'Account\']?[\'Name\'], \'\')}'
                  resolution: '@{coalesce(triggerBody()?[\'Resolution\'], \'\')}'
                  owner_name: '@{coalesce(triggerBody()?[\'Owner\']?[\'Name\'], \'\')}'
                  salesforce_id: '@{triggerBody()?[\'Id\']}'
                }
              ]
            }
            authentication: {
              type: 'ManagedServiceIdentity'
              audience: 'https://search.azure.com'
            }
          }
          runAfter: {
            Generate_Embeddings: ['Succeeded']
          }
        }
      }
    }
    parameters: {
      '$connections': {
        value: {
          salesforce: {
            connectionId: salesforceConnection.id
            connectionName: salesforceConnection.name
            id: subscriptionResourceId('Microsoft.Web/locations/managedApis', location, 'salesforce')
          }
        }
      }
    }
  }
}

// // Logic App -> Cognitive Services OpenAI User (for embeddings via Managed Identity)
// resource logicAppOpenAIRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
//   scope: aiFoundry
//   name: 'a1b2c3d4-1001-4000-8000-000000000009'
//   properties: {
//     principalId: logicApp.identity.principalId
//     roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd')
//     principalType: 'ServicePrincipal'
//   }
// }

// // Logic App -> Search Index Data Contributor (for indexing via Managed Identity)
// resource logicAppSearchRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
//   scope: aiSearch
//   name: 'a1b2c3d4-1001-4000-8000-00000000000a'
//   properties: {
//     principalId: logicApp.identity.principalId
//     roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '8ebe5a00-799e-43f5-93ac-243d3dce84a7')
//     principalType: 'ServicePrincipal'
//   }
// }

// // Logic App -> Search Service Contributor (for managing indexes via Managed Identity)
// resource logicAppSearchServiceRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
//   scope: aiSearch
//   name: 'a1b2c3d4-1001-4000-8000-00000000000b'
//   properties: {
//     principalId: logicApp.identity.principalId
//     roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7ca78c08-252a-4471-8644-bb5ff32d4ba0')
//     principalType: 'ServicePrincipal'
//   }
// }

// ============================================================================
// Outputs
// ============================================================================

output aiFoundryName string = aiFoundry.name
output aiFoundryEndpoint string = aiFoundry.properties.endpoint
output aiOpenAIEndpoint string = 'https://${aiFoundry.name}.openai.azure.com/'
output aiProjectName string = aiProject.name
output aiProjectEndpoint string = 'https://${aiFoundry.name}.services.ai.azure.com/api/projects/${aiProject.name}'
output aiProjectConnectionString string = '${location}.api.azureml.ms;${subscription().subscriptionId};${resourceGroup().name};${aiProject.name}'
output aiSearchName string = aiSearch.name
output aiSearchEndpoint string = 'https://${aiSearch.name}.search.windows.net'
output appInsightsName string = appInsights.name
output appInsightsConnectionString string = appInsights.properties.ConnectionString
output modelDeploymentName string = modelDeployment.name
output logicAppName string = logicApp.name
output logicAppId string = logicApp.id
output logicAppUpdateName string = logicAppUpdate.name
output logicAppUpdateId string = logicAppUpdate.id
output salesforceConnectionName string = salesforceConnection.name
output salesforceConnectionId string = salesforceConnection.id
output logAnalyticsWorkspaceId string = logAnalytics.id
