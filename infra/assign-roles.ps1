# Role Assignment Script
# Run this to create all role assignments via CLI (bypasses Bicep conflicts)
# Update $rg, $foundryScope, and $searchScope to match your deployment before running.

$ErrorActionPreference = "Stop"
$rg = "<your-resource-group>"

# Get resource principal IDs
Write-Host "Fetching resource identities..." -ForegroundColor Cyan
$aiFoundryPrincipal = az resource list -g $rg --resource-type "Microsoft.CognitiveServices/accounts" --query "[?kind=='AIServices'].identity.principalId" -o tsv
$projectPrincipal = az resource list -g $rg --resource-type "Microsoft.CognitiveServices/accounts/projects" --query "[0].identity.principalId" -o tsv
$logicAppPrincipal = az resource list -g $rg --resource-type "Microsoft.Logic/workflows" --query "[?contains(name,'salesforce')].identity.principalId | [0]" -o tsv
$logicAppUpdatePrincipal = az resource list -g $rg --resource-type "Microsoft.Logic/workflows" --query "[?contains(name,'sf-update')].identity.principalId | [0]" -o tsv
$userPrincipal = az ad signed-in-user show --query id -o tsv

Write-Host "  AI Foundry:  $aiFoundryPrincipal" -ForegroundColor Gray
Write-Host "  AI Project:  $projectPrincipal" -ForegroundColor Gray
Write-Host "  Logic App:   $logicAppPrincipal" -ForegroundColor Gray
Write-Host "  Logic App (Update): $logicAppUpdatePrincipal" -ForegroundColor Gray
Write-Host "  User:        $userPrincipal" -ForegroundColor Gray

$subscriptionId = (az account show --query id -o tsv)
$foundryName = (az resource list -g $rg --resource-type "Microsoft.CognitiveServices/accounts" --query "[?kind=='AIServices'].name" -o tsv)
$searchName = (az resource list -g $rg --resource-type "Microsoft.Search/searchServices" --query "[0].name" -o tsv)
$foundryScope = "/subscriptions/$subscriptionId/resourceGroups/$rg/providers/Microsoft.CognitiveServices/accounts/$foundryName"
$searchScope = "/subscriptions/$subscriptionId/resourceGroups/$rg/providers/Microsoft.Search/searchServices/$searchName"

function Assign-Role($principal, $principalType, $role, $scope, $description) {
    Write-Host "  $description" -ForegroundColor Yellow -NoNewline
    $existing = az role assignment list --assignee $principal --role $role --scope $scope -o json 2>$null | ConvertFrom-Json
    if ($existing.Count -gt 0) {
        Write-Host " [already exists]" -ForegroundColor DarkGray
    } else {
        az role assignment create --assignee-object-id $principal --assignee-principal-type $principalType --role $role --scope $scope -o none 2>$null
        Write-Host " [created]" -ForegroundColor Green
    }
}

Write-Host "`nAssigning roles..." -ForegroundColor Cyan

# AI Foundry -> Search
Assign-Role $aiFoundryPrincipal "ServicePrincipal" "Search Index Data Contributor" $searchScope "AI Foundry -> Search Index Data Contributor"

# Search MI -> AI Foundry: Cognitive Services OpenAI User
# Required so the Search service can call AOAI chat/completions for the Foundry
# knowledge base's model query planning + semantic ranking inside knowledge_base_retrieve.
# This is the ONLY role required for AAD inference.
$searchPrincipal = az resource list -g $rg --resource-type "Microsoft.Search/searchServices" --query "[0].identity.principalId" -o tsv
Write-Host "  Search:      $searchPrincipal" -ForegroundColor Gray
Assign-Role $searchPrincipal "ServicePrincipal" "Cognitive Services OpenAI User" $foundryScope "Search -> Cognitive Services OpenAI User"

# AI Project -> Foundry
Assign-Role $projectPrincipal "ServicePrincipal" "Azure AI User" $foundryScope "AI Project -> Azure AI User"
Assign-Role $projectPrincipal "ServicePrincipal" "Azure AI Project Manager" $foundryScope "AI Project -> Azure AI Project Manager"

# AI Project -> Search
Assign-Role $projectPrincipal "ServicePrincipal" "Search Index Data Reader" $searchScope "AI Project -> Search Index Data Reader"

# Logic App -> Foundry
Assign-Role $logicAppPrincipal "ServicePrincipal" "Cognitive Services OpenAI User" $foundryScope "Logic App -> Cognitive Services OpenAI User"

# Logic App -> Search
Assign-Role $logicAppPrincipal "ServicePrincipal" "Search Index Data Contributor" $searchScope "Logic App -> Search Index Data Contributor"
Assign-Role $logicAppPrincipal "ServicePrincipal" "Search Service Contributor" $searchScope "Logic App -> Search Service Contributor"

# Logic App (Update) -> Foundry
Assign-Role $logicAppUpdatePrincipal "ServicePrincipal" "Cognitive Services OpenAI User" $foundryScope "Logic App (Update) -> Cognitive Services OpenAI User"

# Logic App (Update) -> Search
Assign-Role $logicAppUpdatePrincipal "ServicePrincipal" "Search Index Data Contributor" $searchScope "Logic App (Update) -> Search Index Data Contributor"
Assign-Role $logicAppUpdatePrincipal "ServicePrincipal" "Search Service Contributor" $searchScope "Logic App (Update) -> Search Service Contributor"

# User -> Foundry & Search (for local dev)
Assign-Role $userPrincipal "User" "Cognitive Services OpenAI User" $foundryScope "User -> Cognitive Services OpenAI User"
Assign-Role $userPrincipal "User" "Search Index Data Contributor" $searchScope "User -> Search Index Data Contributor"

Write-Host "`nDone! All role assignments are in place." -ForegroundColor Green
