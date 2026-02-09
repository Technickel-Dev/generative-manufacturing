# Generative Manufacturing MCP Server

This is the backend MCP server for the Generative Manufacturing demo. It interfaces with Prusa printers (or a mock one), runs the slicer, and handles Gemini analysis.

## Prerequisites

- **Python 3.10+** (managed with `uv` recommended)
- **OpenSCAD**: Must be installed and available in your system PATH.
- **PrusaSlicer**: Must be installed and available in your system PATH.
- **Google Cloud SDK**: optional, for deployment.

## Installation & Running Locally

1.  **Clone the repository** (if you haven't already).
2.  **Navigate to this directory**: `cd generative-manufacturing-server`
3.  **Install dependencies**:
    ```bash
    uv sync
    ```
4.  **Configure Environment**:
    Copy the `.env.example` file as a `.env` file and update the values with your own.
5.  **Run the server**:
    ```bash
    uv run server.py
    ```
    The server will start on port 3001 (or as defined by `PORT` env var).

## Configuration

| Variable | Description | Default |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | API Key for Gemini 3 | Required |
| `PRINTER_IP` | IP address of the Prusa Printer | `127.0.0.1` |
| `PRINTER_API_KEY` | API Key for Prusa Connect/Local | `dummy_key` |
| `CAMERA_URL` | RTSP/HTTP URL for printer camera | `None` |
| `MOCK_MODE` | Enable mock mode (no hardware needed) | `false` |
| `HOST` | Host to bind to | `0.0.0.0` |
| `PORT` | Port to bind to | `3001` |
| `GCS_BUCKET_NAME` | Bucket for storing captures (optional) | `None` |

## Tools Available

This MCP server exposes the following tools:

### Generative Design
*   `generate_model`: Generate a 3D model (STL) from a text description using OpenSCAD.

### Slicing & Printing
*   `list_stl_files`: List available STL files in the local models directory.
*   `slice_model`: Slice a 3D model (STL) into G-code with specific settings.
*   `list_gcode_files`: List available G-code files ready for printing.
*   `upload_model`: Upload a G-code file to the printer.
*   `start_print`: Start a print job for an uploaded file.

### Printer Control
*   `show_printer_dashboard`: Fetch the latest raw printer data for the dashboard UI.
*   `get_printer_status`: Get the current status of the printer (temperatures, progress).
*   `get_printer_info`: Get basic information about the connected printer.
*   `pause_printer`: Pause the current print job.
*   `resume_printer`: Resume the current print job.
*   `stop_printer`: Stop the current print job.

### Monitor & Analysis
*   `get_camera_frame`: Take a screenshot from the printer camera.
*   `quick_print_check`: Perform a quick status check using Gemini 3 Vision (Low thinking).
*   `deep_print_check`: Perform a deep, complex diagnosis of a potential failure using Gemini 3 Vision (High thinking).
*   `simulate_spaghetti_incident`: Simulate a failure incident for testing the UI.
*   `review_latest_incident`: Review a detected incident report and SOPs.

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
