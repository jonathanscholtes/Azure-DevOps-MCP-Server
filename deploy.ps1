param (
    [string]$Subscription,
    [string]$Location = "eastus2"
)


Write-Host "Subscription: $Subscription"
Write-Host "Location: $Location"


# Variables
$projectName = "adomcp"
$environmentName = "demo"
$timestamp = Get-Date -Format "yyyyMMddHHmmss"

function Get-RandomAlphaNumeric {
    param (
        [int]$Length = 12,
        [string]$Seed
    )

    $base62Chars = "abcdefghijklmnopqrstuvwxyz123456789"

    # Convert the seed string to a hash (e.g., MD5)
    $md5 = [System.Security.Cryptography.MD5]::Create()
    $seedBytes = [System.Text.Encoding]::UTF8.GetBytes($Seed)
    $hashBytes = $md5.ComputeHash($seedBytes)

    # Use bytes from hash to generate characters
    $randomString = ""
    for ($i = 0; $i -lt $Length; $i++) {
        $index = $hashBytes[$i % $hashBytes.Length] % $base62Chars.Length
        $randomString += $base62Chars[$index]
    }

    return $randomString
}

# Example usage: Generate a resource token based on a seed
$resourceToken = Get-RandomAlphaNumeric -Length 12 -Seed $timestamp

# Clear account context and configure Azure CLI settings
az account clear
az config set core.enable_broker_on_windows=false
az config set core.login_experience_v2=off

# Login to Azure
az login 
az account set --subscription $Subscription


$deploymentNameInfra = "deployment-ado-mcp-$resourceToken"
$templateFile = "infra/main.bicep"

$deploymentOutput = az deployment sub create `
    --name $deploymentNameInfra `
    --location $Location `
    --template-file $templateFile `
    --parameters `
        environmentName=$environmentName `
        projectName=$projectName `
        resourceToken=$resourceToken `
        location=$Location `
    --query "properties.outputs"


# Parse deployment outputs
$deploymentOutputJsonInfra = $deploymentOutput | ConvertFrom-Json
$managedIdentityName = $deploymentOutputJsonInfra.managedIdentityName.value
$appServicePlanName = $deploymentOutputJsonInfra.appServicePlanName.value
$resourceGroupName = $deploymentOutputJsonInfra.resourceGroupName.value
$logAnalyticsWorkspaceName = $deploymentOutputJsonInfra.logAnalyticsWorkspaceName.value
$applicationInsightsName = $deploymentOutputJsonInfra.applicationInsightsName.value
$keyVaultName = $deploymentOutputJsonInfra.keyVaultName.value
$containerRegistryName = $deploymentOutputJsonInfra.containerRegistryName.value

# Step 1: Build Images

Write-Host "=== Building Images for MCP Server ==="
Write-Host "Using ACR: $containerRegistryName"
Write-Host "Resource Group: $resourceGroupName`n"

# Define image names and paths
$images = @(
    @{ name = "ado-mcp"; path = ".\src\mcp\ado" }
)

# Build images
foreach ($image in $images) {
    Write-Host "Building image '$($image.name):latest' from '$($image.path)'..."
    Write-Host "az acr build --resource-group $resourceGroupName --registry $containerRegistryName --image $($image.name):latest $image.path"

    az acr build `
        --resource-group $resourceGroupName `
        --registry $containerRegistryName `
        --image "$($image.name):latest" `
        $image.path
}


# Step 2: Deploy Apps
$deploymentNameApps = "deployment-do-mcp-$resourceToken"
$appsTemplateFile = "infra/app/main.bicep"
$deploymentOutputApps = az deployment sub create  `
    --name $deploymentNameApps `
    --location $Location `
    --template-file $appsTemplateFile `
    --parameters `
        environmentName=$environmentName `
        projectName=$projectName `
        location=$Location `
        resourceGroupName=$resourceGroupName `
        resourceToken=$resourceToken `
        managedIdentityName=$managedIdentityName `
        logAnalyticsWorkspaceName=$logAnalyticsWorkspaceName `
        appInsightsName=$applicationInsightsName `
        appServicePlanName=$appServicePlanName `
        containerRegistryName=$containerRegistryName `
    --query "properties.outputs"


$deploymentOutputJson = $deploymentOutputApps | ConvertFrom-Json




Write-Host "`n✅ Deployment Complete!"


