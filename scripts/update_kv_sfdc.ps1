$ErrorActionPreference = 'Stop'
$envPath = Join-Path $PSScriptRoot '..\.env'
$envMap = @{}
Get-Content $envPath | ForEach-Object {
    if ($_ -match '^([^=#]+)=(.*)$') { $envMap[$matches[1]] = $matches[2] }
}
$vault = 'il-demo-apim-kv'
az keyvault secret set --vault-name $vault --name salesforce-client-id      --value $envMap['SFDC_CLIENT_ID']             -o none
az keyvault secret set --vault-name $vault --name salesforce-client-secret  --value $envMap['SFDC_CLIENT_SECRET']         -o none
az keyvault secret set --vault-name $vault --name salesforce-token-endpoint --value $envMap['SALESFORCE_TOKEN_ENDPOINT']  -o none
foreach ($n in @('salesforce-client-id','salesforce-client-secret','salesforce-token-endpoint')) {
    $u = az keyvault secret show --vault-name $vault --name $n --query 'attributes.updated' -o tsv
    Write-Host "$n updated $u"
}
