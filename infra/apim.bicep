// ============================================================================
// NimbusCloud Helpdesk Demo - Azure API Management (APIM) Instance
// Exposes CRM Case Creation as a NATIVE MCP Server
// Uses "REST API as MCP server" feature — API operations become MCP tools
// ============================================================================

param environmentName string
param location string
param principalId string

@secure()
@description('Salesforce OAuth Client ID')
param salesforceClientId string

@secure()
@description('Salesforce OAuth Client Secret')
param salesforceClientSecret string

@description('Salesforce OAuth Token Endpoint')
param salesforceTokenEndpoint string

// ============================================================================
// APIM Instance
// ============================================================================

resource apim 'Microsoft.ApiManagement/service@2024-06-01-preview' = {
  name: '${environmentName}-apim'
  location: location
  sku: {
    name: 'Developer'
    capacity: 1
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    publisherEmail: 'admin@${environmentName}.local'
    publisherName: 'NimbusCloud Helpdesk Demo'
  }
}

// ============================================================================
// Key Vault - Securely store Salesforce OAuth credentials
// ============================================================================

resource kv 'Microsoft.KeyVault/vaults@2023-02-01' = {
  name: '${environmentName}-apim-kv'
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    accessPolicies: [
      {
        tenantId: subscription().tenantId
        objectId: principalId
        permissions: {
          secrets: [ 'get', 'list', 'set' ]
        }
      }
      {
        tenantId: subscription().tenantId
        objectId: apim.identity.principalId
        permissions: {
          secrets: [ 'get' ]
        }
      }
    ]
    enableSoftDelete: true
    enablePurgeProtection: true
  }
}

// Key Vault Secrets
resource clientIdSecret 'Microsoft.KeyVault/vaults/secrets@2023-02-01' = {
  parent: kv
  name: 'salesforce-client-id'
  properties: {
    value: salesforceClientId
  }
}

resource clientSecretSecret 'Microsoft.KeyVault/vaults/secrets@2023-02-01' = {
  parent: kv
  name: 'salesforce-client-secret'
  properties: {
    value: salesforceClientSecret
  }
}

resource tokenEndpointSecret 'Microsoft.KeyVault/vaults/secrets@2023-02-01' = {
  parent: kv
  name: 'salesforce-token-endpoint'
  properties: {
    value: salesforceTokenEndpoint
  }
}

// ============================================================================
// APIM Named Values (pull from Key Vault)
// ============================================================================

resource namedValueClientId 'Microsoft.ApiManagement/service/namedValues@2024-06-01-preview' = {
  parent: apim
  name: 'salesforce-client-id'
  properties: {
    displayName: 'salesforce-client-id'
    secret: true
    keyVault: {
      secretIdentifier: '${kv.properties.vaultUri}secrets/salesforce-client-id'
    }
  }
  dependsOn: [ clientIdSecret ]
}

resource namedValueClientSecret 'Microsoft.ApiManagement/service/namedValues@2024-06-01-preview' = {
  parent: apim
  name: 'salesforce-client-secret'
  properties: {
    displayName: 'salesforce-client-secret'
    secret: true
    keyVault: {
      secretIdentifier: '${kv.properties.vaultUri}secrets/salesforce-client-secret'
    }
  }
  dependsOn: [ clientSecretSecret ]
}

resource namedValueTokenEndpoint 'Microsoft.ApiManagement/service/namedValues@2024-06-01-preview' = {
  parent: apim
  name: 'salesforce-token-endpoint'
  properties: {
    displayName: 'salesforce-token-endpoint'
    secret: true
    keyVault: {
      secretIdentifier: '${kv.properties.vaultUri}secrets/salesforce-token-endpoint'
    }
  }
  dependsOn: [ tokenEndpointSecret ]
}

// ============================================================================
// REST API - Salesforce Case Operations
// This API will be exposed as an MCP server via the native APIM feature
// ============================================================================

resource salesforceApi 'Microsoft.ApiManagement/service/apis@2024-06-01-preview' = {
  parent: apim
  name: 'salesforce-case-api'
  properties: {
    displayName: 'Salesforce Case API'
    description: 'REST API for Salesforce Case operations. Exposed as MCP server for AI agents.'
    path: 'salesforce'
    protocols: [ 'https' ]
    subscriptionRequired: true  // Key-based auth for Foundry MCPTool
    subscriptionKeyParameterNames: {
      header: 'Ocp-Apim-Subscription-Key'
      query: 'subscription-key'
    }
    apiRevision: '1'
    isCurrent: true
  }
  dependsOn: [ namedValueClientId, namedValueClientSecret, namedValueTokenEndpoint ]
}

// Schema for the Create Case request body (used by MCP tool to generate input parameters)
resource createCaseSchema 'Microsoft.ApiManagement/service/apis/schemas@2024-06-01-preview' = {
  parent: salesforceApi
  name: 'create-case-schema'
  properties: {
    contentType: 'application/vnd.oai.openapi.components+json'
    document: {
      components: {
        schemas: {
          CreateCaseRequest: {
            type: 'object'
            properties: {
              subject: {
                type: 'string'
                description: 'Brief summary of the case issue (required, max 100 chars)'
              }
              description: {
                type: 'string'
                description: 'Detailed description of the case including any relevant KB article references'
              }
              priority: {
                type: 'string'
                enum: ['Low', 'Medium', 'High']
                description: 'Case priority based on urgency. Default: Medium'
              }
              origin: {
                type: 'string'
                enum: ['Web', 'Phone', 'Email']
                description: 'How the case was submitted. Default: Web'
              }
              status: {
                type: 'string'
                enum: ['New', 'Working', 'Escalated']
                description: 'Initial case status. Default: New'
              }
            }
            required: ['subject']
          }
        }
      }
    }
  }
}

// POST /cases - Create a Salesforce Case
resource createCaseOperation 'Microsoft.ApiManagement/service/apis/operations@2024-06-01-preview' = {
  parent: salesforceApi
  name: 'create-case'
  properties: {
    displayName: 'Create Salesforce Case'
    description: 'Create a support case in Salesforce. Use this when a customer service representative requests to create a support ticket, file a case, or escalate an issue.'
    method: 'POST'
    urlTemplate: '/cases'
    request: {
      representations: [
        {
          contentType: 'application/json'
          schemaId: createCaseSchema.name
          typeName: 'CreateCaseRequest'
        }
      ]
    }
    responses: [
      {
        statusCode: 201
        description: 'Case created successfully'
        representations: [
          {
            contentType: 'application/json'
          }
        ]
      }
      {
        statusCode: 400
        description: 'Invalid request'
      }
    ]
  }
}

// ============================================================================
// Operation Policy — Salesforce OAuth + Case Creation
// ============================================================================

resource createCasePolicy 'Microsoft.ApiManagement/service/apis/operations/policies@2024-06-01-preview' = {
  parent: createCaseOperation
  name: 'policy'
  properties: {
    format: 'rawxml'
    value: '''<policies>
  <inbound>
    <base />
    <!-- Step 1: Get Salesforce OAuth token -->
    <send-request mode="new" response-variable-name="sf-token-response" timeout="20" ignore-error="false">
      <set-url>{{salesforce-token-endpoint}}</set-url>
      <set-method>POST</set-method>
      <set-header name="Content-Type" exists-action="override">
        <value>application/x-www-form-urlencoded</value>
      </set-header>
      <set-body>grant_type=client_credentials&amp;client_id={{salesforce-client-id}}&amp;client_secret={{salesforce-client-secret}}</set-body>
    </send-request>
    <set-variable name="sf-token-body" value="@(((IResponse)context.Variables["sf-token-response"]).Body.As<JObject>())" />
    <set-variable name="sf-access-token" value="@((string)((JObject)context.Variables["sf-token-body"])["access_token"])" />
    <set-variable name="sf-instance-url" value="@((string)((JObject)context.Variables["sf-token-body"])["instance_url"])" />
    <!-- Step 2: Build Salesforce Case payload from request body -->
    <set-variable name="sf-case-body" value="@{
      var req = context.Request.Body.As<JObject>();
      var sfCase = new JObject();
      sfCase["Subject"] = (string)req["subject"] ?? "No subject";
      if (req["description"] != null) { sfCase["Description"] = (string)req["description"]; }
      sfCase["Priority"] = (string)req["priority"] ?? "Medium";
      sfCase["Origin"] = (string)req["origin"] ?? "Web";
      sfCase["Status"] = (string)req["status"] ?? "New";
      return sfCase.ToString();
    }" />
    <!-- Step 3: POST to Salesforce -->
    <send-request mode="new" response-variable-name="sf-case-response" timeout="30" ignore-error="false">
      <set-url>@($"{(string)context.Variables["sf-instance-url"]}/services/data/v62.0/sobjects/Case")</set-url>
      <set-method>POST</set-method>
      <set-header name="Authorization" exists-action="override">
        <value>@($"Bearer {(string)context.Variables["sf-access-token"]}")</value>
      </set-header>
      <set-header name="Content-Type" exists-action="override">
        <value>application/json</value>
      </set-header>
      <set-body>@((string)context.Variables["sf-case-body"])</set-body>
    </send-request>
    <!-- Step 4: Return response -->
    <return-response>
      <set-status code="@(((IResponse)context.Variables["sf-case-response"]).StatusCode)" />
      <set-header name="Content-Type" exists-action="override">
        <value>application/json</value>
      </set-header>
      <set-body>@{
        var sfResp = ((IResponse)context.Variables["sf-case-response"]);
        var sfBody = sfResp.Body.As<JObject>();
        var statusCode = sfResp.StatusCode;
        
        if (statusCode >= 200 && statusCode < 300) {
          return new JObject(
            new JProperty("success", true),
            new JProperty("case_id", (string)sfBody["id"]),
            new JProperty("message", "Case created successfully in Salesforce")
          ).ToString();
        } else {
          return new JObject(
            new JProperty("success", false),
            new JProperty("error", sfBody.ToString()),
            new JProperty("status_code", statusCode)
          ).ToString();
        }
      }</set-body>
    </return-response>
  </inbound>
  <backend>
    <base />
  </backend>
  <outbound>
    <base />
  </outbound>
  <on-error>
    <base />
  </on-error>
</policies>'''
  }
}

// ============================================================================
// Product & Subscription — Key-based auth for Foundry agents
// ============================================================================

resource foundryProduct 'Microsoft.ApiManagement/service/products@2024-06-01-preview' = {
  parent: apim
  name: 'foundry-agents'
  properties: {
    displayName: 'Foundry Agents'
    description: 'Product for AI Foundry agents to access the Salesforce Case MCP tools'
    subscriptionRequired: true
    approvalRequired: false
    state: 'published'
  }
}

resource foundryProductApi 'Microsoft.ApiManagement/service/products/apis@2024-06-01-preview' = {
  parent: foundryProduct
  name: salesforceApi.name
}

// Note: The MCP server (salesforce-case-mcp-apim) is created via the Azure portal
// and must also be added to this product manually or via az rest:
//   az rest --method put --url ".../products/foundry-agents/apis/salesforce-case-mcp-apim?api-version=2024-06-01-preview" --body "{}"

resource foundrySubscription 'Microsoft.ApiManagement/service/subscriptions@2024-06-01-preview' = {
  parent: apim
  name: 'foundry-subscription'
  properties: {
    displayName: 'Foundry Agent Subscription'
    scope: '/products/${foundryProduct.name}'
    state: 'active'
  }
}

// ============================================================================
// Outputs
// ============================================================================

output apimEndpoint string = 'https://${apim.name}.azure-api.net'
output apimMcpServerPath string = '/salesforce'
output apimName string = apim.name
output keyVaultName string = kv.name
output subscriptionId string = foundrySubscription.id
