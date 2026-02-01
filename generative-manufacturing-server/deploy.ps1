$serviceName = "generative-manufacturing-server"
$region = "us-east1"

Write-Host "Deploying $serviceName to Cloud Run..."

gcloud run deploy $serviceName `
  --source . `
  --region $region `
  --allow-unauthenticated `
  --set-env-vars="MOCK_MODE=true" `
  --set-secrets="GEMINI_API_KEY=GEMINI_API_KEY:latest"

if ($LASTEXITCODE -ne 0) {
    Write-Error "Deployment failed."
    exit 1
}

Write-Host "Deployment complete."
