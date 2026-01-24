#!/usr/bin/env uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "mcp @ git+https://github.com/modelcontextprotocol/python-sdk@main",
#     "qrcode[pil]>=8.0",
#     "uvicorn>=0.34.0",
#     "starlette>=0.46.0",
# ]
# ///

import os
from dotenv import load_dotenv
import json

import uvicorn
from mcp.server.fastmcp import FastMCP
from mcp import types
from starlette.middleware.cors import CORSMiddleware

from prusa_printer import PrusaPrinter

# Load environment variables
load_dotenv()

# Initialize Printer Client
PRINTER_IP = os.getenv("PRINTER_IP", "127.0.0.1")
PRINTER_API_KEY = os.getenv("PRINTER_API_KEY", "dummy_key")

printer = PrusaPrinter(ip=PRINTER_IP, api_key=PRINTER_API_KEY)

# Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "3109"))

# Initialize FastMCP Server
mcp = FastMCP(
  "Generative Manufacturing",
)

DASHBOARD_URI = "ui://printer-dashboard.html"

@mcp.resource(
    DASHBOARD_URI,
    mime_type="text/html;profile=mcp-app",
    meta={"ui": {"csp": {"resourceDomains": ["https://unpkg.com", "https://fonts.googleapis.com", "https://fonts.gstatic.com"]}}},
)
def printer_dashboard() -> str:
    """Dashboard HTML resource with CSP metadata for external dependencies."""
    
    dashboard_path = os.path.join(os.path.dirname(__file__), "resources/printer-dashboard.html")
    try:
        with open(dashboard_path, "r", encoding="utf-8") as f:
            dashboard_html = f.read()
    except FileNotFoundError:
        print(f"Warning: printer-dashboard.html not found at {dashboard_path}")
        dashboard_html = "<html><body><h1>Error: dashboard.html not found</h1></body></html>"
    
    
    return dashboard_html

@mcp.tool(meta={
    "ui":{
        "resourceUri": DASHBOARD_URI
    }
})
async def show_printer_dashboard() -> list[types.TextContent]:
    """
    Fetch the latest raw printer data for the dashboard.
    """
    try:
        # Fetch both info and status
        info = await printer.get_info()
        status = await printer.get_status()
        
        # Combine data for dashboard
        dashboard_data = {
            "name": info.get("name", "Unknown"),
            "model": info.get("model", "Unknown"),
            "firmware": info.get("firmware", "Unknown"),
            "state": status.get("state", "Unknown"),
            "temp_nozzle": status.get("temp_nozzle", 0),
            "target_nozzle": status.get("target_nozzle", 0),
            "temp_bed": status.get("temp_bed", 0),
            "target_bed": status.get("target_bed", 0),
            "temp_chamber": status.get("temp_chamber", 0),
            "target_chamber": status.get("target_chamber", 0),
            "progress": status.get("progress", 0),
            "time_remaining": status.get("time_remaining", 0),
            "print_time": status.get("print_time", 0),
        }
        
        return [types.TextContent(type="text", text=json.dumps(dashboard_data), mimeType="application/json")]
    except Exception as e:
        error_data = {"error": f"Error fetching printer data: {str(e)}"}
        return [types.TextContent(type="text", text=json.dumps(error_data))]

@mcp.tool()
async def get_printer_status() -> str:
    """
    Get the current status of the printer including temperatures and progress.
    """
    try:
        status = await printer.get_status()
        return (f"State: {status['state']}\n"
                f"Nozzle: {status['temp_nozzle']}°C / {status['target_nozzle']}°C\n"
                f"Bed: {status['temp_bed']}°C / {status['target_bed']}°C\n"
                f"Chamber: {status['temp_chamber']}°C / {status['target_chamber']}°C\n"
                f"Progress: {status['progress']}%\n"
                f"Time Remaining: {status['time_remaining']}")
    except Exception as e:
        return f"Error fetching printer status: {str(e)}"

@mcp.tool()
async def get_printer_info() -> str:
    """
    Get basic information about the connected Prusa printer (Model, Serial, Firmware).
    """
    try:
        info = await printer.get_info()
        return f"Printer: {info['name']} ({info['model']})\nFirmware: {info['firmware']}\nState: {info['state']}"
    except Exception as e:
        return f"Error fetching printer info: {str(e)}"

if __name__ == "__main__":
    app = mcp.streamable_http_app(stateless_http=True)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    print(f"QR Code Server listening on http://{HOST}:{PORT}/mcp")
    uvicorn.run(app, host=HOST, port=PORT)
