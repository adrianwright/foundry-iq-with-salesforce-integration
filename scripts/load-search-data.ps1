# load-search-data.ps1
# Assigns required RBAC roles and runs the AI Search data loaders.
# Usage: .\scripts\load-search-data.ps1

param(
    [string]$ResourceGroup = (azd env get-value AZURE_RESOURCE_GROUP 2>$null),
    [string]$PythonExe = ".venv/Scripts/python.exe"
)

$ErrorActionPreference = "Stop"

if (-not $ResourceGroup) {
    Write-Host "ERROR: Could not determine resource group. Pass -ResourceGroup or run 'azd env get-value AZURE_RESOURCE_GROUP'." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  AI Search Data Loader" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# --- Resolve resources ---
Write-Host "Resolving resources in '$ResourceGroup'..." -ForegroundColor Yellow
$subscriptionId = az account show --query id -o tsv
$searchName = az resource list -g $ResourceGroup --resource-type "Microsoft.Search/searchServices" --query "[0].name" -o tsv
$aoaiName = az resource list -g $ResourceGroup --resource-type "Microsoft.CognitiveServices/accounts" --query "[0].name" -o tsv

if (-not $searchName) {
    Write-Host "ERROR: No AI Search service found in '$ResourceGroup'." -ForegroundColor Red
    exit 1
}
if (-not $aoaiName) {
    Write-Host "ERROR: No Cognitive Services / AI Services account found in '$ResourceGroup'." -ForegroundColor Red
    exit 1
}

$searchScope = "/subscriptions/$subscriptionId/resourceGroups/$ResourceGroup/providers/Microsoft.Search/searchServices/$searchName"
$aoaiScope = "/subscriptions/$subscriptionId/resourceGroups/$ResourceGroup/providers/Microsoft.CognitiveServices/accounts/$aoaiName"
Write-Host "  Search Service: $searchName" -ForegroundColor Gray
Write-Host "  AI Services:    $aoaiName" -ForegroundColor Gray

# --- Validate embedding model deployment ---
Write-Host ""
Write-Host "Validating embedding model deployment..." -ForegroundColor Yellow
$embedding = az cognitiveservices account deployment list --name $aoaiName --resource-group $ResourceGroup --query "[?properties.model.name=='text-embedding-3-small'].name" -o tsv
if (-not $embedding) {
    Write-Host "ERROR: No 'text-embedding-3-small' deployment found on '$aoaiName'." -ForegroundColor Red
    Write-Host "       Create one via the Foundry/AOAI portal or Bicep before running this script." -ForegroundColor Red
    exit 1
}
Write-Host "  text-embedding-3-small [present]" -ForegroundColor Green

# --- Assign RBAC roles ---
Write-Host ""
Write-Host "Assigning RBAC roles to current user..." -ForegroundColor Yellow
$userPrincipal = az ad signed-in-user show --query id -o tsv
Write-Host "  User: $userPrincipal" -ForegroundColor Gray

# Note: AI Services (kind=AIServices) data plane requires all three Cognitive roles below.
# 'Cognitive Services OpenAI User' alone returns 401 PermissionDenied on /embeddings.
$roleAssignments = @(
    @{ Role = "Search Service Contributor";       Scope = $searchScope },
    @{ Role = "Search Index Data Contributor";    Scope = $searchScope },
    @{ Role = "Cognitive Services OpenAI User";   Scope = $aoaiScope },
    @{ Role = "Cognitive Services User";          Scope = $aoaiScope },
    @{ Role = "Azure AI Developer";               Scope = $aoaiScope }
)

foreach ($ra in $roleAssignments) {
    $existing = az role assignment list --assignee $userPrincipal --role $ra.Role --scope $ra.Scope -o json 2>$null | ConvertFrom-Json
    if ($existing.Count -gt 0) {
        Write-Host "  $($ra.Role) [already assigned]" -ForegroundColor DarkGray
    } else {
        az role assignment create --assignee-object-id $userPrincipal --assignee-principal-type User --role $ra.Role --scope $ra.Scope -o none 2>$null
        Write-Host "  $($ra.Role) [assigned]" -ForegroundColor Green
    }
}

# RBAC propagation: AI Services data plane is slower than ARM (often 2-3 min).
Write-Host ""
Write-Host "Waiting 180s for RBAC propagation (AI Services data plane is slower than ARM)..." -ForegroundColor Yellow
Start-Sleep -Seconds 180

# --- Install Python dependencies ---
Write-Host ""
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
& $PythonExe -m pip install -r scripts/requirements.txt --quiet

# --- Run loaders ---
Write-Host ""
Write-Host "Loading knowledge base articles..." -ForegroundColor Cyan
& $PythonExe scripts/load_knowledge_base.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: load_knowledge_base.py failed." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Loading forum posts..." -ForegroundColor Cyan
& $PythonExe scripts/load_forum_posts.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: load_forum_posts.py failed." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Loading service cases..." -ForegroundColor Cyan
& $PythonExe scripts/load_cases.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: load_cases.py failed." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  All data loaded successfully!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Indexes populated:" -ForegroundColor White
Write-Host "  - helpdesk-knowledge    (KB articles)" -ForegroundColor White
Write-Host "  - community-forum-posts (forum posts)" -ForegroundColor White
Write-Host "  - service-cases         (support cases)" -ForegroundColor White
Write-Host ""
