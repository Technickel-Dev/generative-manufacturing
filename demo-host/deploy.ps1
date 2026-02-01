$ErrorActionPreference = "Stop"

# Configuration
$region = "us-east1"

# Get Project ID
Write-Host "Getting Google Cloud Project ID..."
$projectId = gcloud config get-value project
if (-not $projectId) {
    Write-Error "No Google Cloud project configured. Run 'gcloud config set project <PROJECT_ID>' first."
    exit 1
}

$imageName = "gcr.io/$projectId/demo-host"

Write-Host "Deploying demo-host to project $projectId in $region..."

# 1. Build
Write-Host "Building container image (this may take a few minutes)..."
gcloud builds submit --tag $imageName .

if ($LASTEXITCODE -ne 0) {
    Write-Error "Build failed."
    exit 1
}

# 2. Deploy Sandbox
Write-Host "Deploying Sandbox service..."
# Use --format to capture just the URL
$sandboxUrl = gcloud run deploy demo-host-sandbox `
  --image $imageName `
  --platform managed `
  --region $region `
  --allow-unauthenticated `
  --set-env-vars MODE=SANDBOX `
  --format="value(status.url)"

if (-not $sandboxUrl) {
    Write-Error "Failed to deploy Sandbox or retrieve URL."
    exit 1
}

$sandboxUrl = $sandboxUrl.Trim()
Write-Host "Sandbox deployed at: $sandboxUrl"

# 3. Deploy Host
Write-Host "Deploying Host service..."
gcloud run deploy demo-host `
  --image $imageName `
  --platform managed `
  --region $region `
  --allow-unauthenticated `
  --set-env-vars "MODE=HOST,SANDBOX_URL=$sandboxUrl,SERVERS=https://generative-manufacturing-server-418864522827.us-east1.run.app/mcp"

if ($LASTEXITCODE -ne 0) {
    Write-Error "Host deployment failed."
    exit 1
}

Write-Host "Deployment complete!"
Write-Host "You can access the Host application at the URL displayed above."
