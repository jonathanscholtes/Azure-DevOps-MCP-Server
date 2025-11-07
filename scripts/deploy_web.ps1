param (
    [string]$webAppName,
    [string]$resourceGroupName,
    [string]$appType,            # "react" or "typescript"
    [string]$appPath,
    [string]$apiURL = "",
    [string]$buildDir = ""       # optional override
)

# Paths
$artifactRoot = "artifacts\$appType"
$nodeTempDir = "$artifactRoot\temp"
$zipFilePath = "$artifactRoot\app.zip"

# Ensure artifacts dir exists
New-Item -ItemType Directory -Force -Path (Split-Path $zipFilePath) | Out-Null

# Handle React app (frontend)
if ($appType -eq "react") {
    $nodeBuildDir = if ($buildDir -ne "") { "${appPath}\${buildDir}" } else { "${appPath}\build" }

    # Only write API_HOST if provided
    if ($apiURL -ne "") {
        Set-Content -Path "$appPath\.env" -Value "REACT_APP_API_HOST=$apiURL"
    } else {
        Write-Host "apiURL not provided; skipping .env configuration."
    }

    # Install & build
    Start-Process "npm.cmd" -ArgumentList "install" -WorkingDirectory $appPath -NoNewWindow -Wait
    Start-Process "npm.cmd" -ArgumentList "run build" -WorkingDirectory $appPath -NoNewWindow -Wait

    # Package build output
    $args = "$nodeBuildDir $zipFilePath $nodeTempDir --exclude_files .env .gitignore *.md"

    Start-Process "python" -ArgumentList "directory_zipper.py $args" -NoNewWindow -Wait
}

# Handle TypeScript app (backend/server)
elseif ($appType -eq "typescript") {
    # Optional API_HOST gets set as app setting instead of .env
    if ($apiURL -ne "") {
        Write-Host "Configuring API_HOST as App Setting..."
        az webapp config appsettings set `
            --resource-group $resourceGroupName `
            --name $webAppName `
            --settings REACT_APP_API_HOST=$apiURL
    }

    # Install & compile TypeScript
    Start-Process "npm.cmd" -ArgumentList "install" -WorkingDirectory $appPath -NoNewWindow -Wait
    Start-Process "npx.cmd" -ArgumentList "tsc" -WorkingDirectory $appPath -NoNewWindow -Wait

    # Collect required files into temp staging dir
    New-Item -ItemType Directory -Force -Path $nodeTempDir | Out-Null
    Copy-Item "$appPath\dist" -Destination $nodeTempDir -Recurse -Force
    Copy-Item "$appPath\node_modules" -Destination $nodeTempDir -Recurse -Force
    Copy-Item "$appPath\package.json" -Destination $nodeTempDir -Force
    if (Test-Path "$appPath\package-lock.json") {
        Copy-Item "$appPath\package-lock.json" -Destination $nodeTempDir -Force
    }

    $zipWorkDir = Join-Path (Split-Path $zipFilePath) "ziptemp"
    if (Test-Path $zipWorkDir) { Remove-Item -Path $zipWorkDir -Recurse -Force -ErrorAction SilentlyContinue }
    New-Item -ItemType Directory -Force -Path $zipWorkDir | Out-Null

    # Construct the argument list for zipper
    $args = "$nodeTempDir $zipFilePath $zipWorkDir --exclude_files .env .gitignore *.md"

    Start-Process "python" -ArgumentList "directory_zipper.py $args" -NoNewWindow -Wait

    # Clean up temp staging directory
    if (Test-Path $nodeTempDir) {
        Remove-Item -Path $nodeTempDir -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "Cleaned up temporary directory: $nodeTempDir"
    }

    if (Test-Path $zipWorkDir) {
        Remove-Item -Path $zipWorkDir -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "Cleaned up zip work directory: $zipWorkDir"
    }
}
else {
    throw "Unsupported appType: $appType. Use 'react' or 'typescript'."
}

# Deploy to Azure Web App
az webapp deploy `
  --resource-group $resourceGroupName `
  --name $webAppName `
  --src-path $zipFilePath `
  --type zip `
  --timeout 60000
