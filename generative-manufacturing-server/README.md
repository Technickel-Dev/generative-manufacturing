# Generative Manufacturing MCP Server

This is the backend MCP server for the Generative Manufacturing demo. It interfaces with Prusa printers (or a mock one), runs the slicer, and handles Gemini analysis.

## Deployment

To deploy this server to Google Cloud Run, run the following command from this directory:

```powershell
gcloud run deploy generative-manufacturing-server `
  --source . `
  --region us-east1 `
  --allow-unauthenticated `
  --set-env-vars="MOCK_MODE=true" `
  --set-secrets="GEMINI_API_KEY=GEMINI_API_KEY:latest"
```

**Note:** Ensure you have the `GEMINI_API_KEY` secret created in Google Cloud Secret Manager.
