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

if (-not $searchName) {
    Write-Host "ERROR: No AI Search service found in '$ResourceGroup'." -ForegroundColor Red
    exit 1
}

$searchScope = "/subscriptions/$subscriptionId/resourceGroups/$ResourceGroup/providers/Microsoft.Search/searchServices/$searchName"
Write-Host "  Search Service: $searchName" -ForegroundColor Gray

# --- Assign RBAC roles ---
Write-Host ""
Write-Host "Assigning RBAC roles to current user..." -ForegroundColor Yellow
$userPrincipal = az ad signed-in-user show --query id -o tsv
Write-Host "  User: $userPrincipal" -ForegroundColor Gray

$roles = @(
    "Search Service Contributor",
    "Search Index Data Contributor"
)

foreach ($role in $roles) {
    $existing = az role assignment list --assignee $userPrincipal --role $role --scope $searchScope -o json 2>$null | ConvertFrom-Json
    if ($existing.Count -gt 0) {
        Write-Host "  $role [already assigned]" -ForegroundColor DarkGray
    } else {
        az role assignment create --assignee-object-id $userPrincipal --assignee-principal-type User --role $role --scope $searchScope -o none 2>$null
        Write-Host "  $role [assigned]" -ForegroundColor Green
    }
}

# Wait briefly for RBAC propagation
Write-Host ""
Write-Host "Waiting 30s for RBAC propagation..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

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
