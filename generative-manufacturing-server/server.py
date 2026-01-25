#!/usr/bin/env uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "mcp @ git+https://github.com/modelcontextprotocol/python-sdk@main",
#     "qrcode[pil]>=8.0",
#     "uvicorn>=0.34.0",
#     "starlette>=0.46.0",
#     "opencv-python>=4.11.0.86",
#     "google-genai",
# ]
# ///

import os
from dotenv import load_dotenv
import json
import base64
import asyncio

import uvicorn
from mcp.server.fastmcp import FastMCP
from mcp import types
from starlette.middleware.cors import CORSMiddleware

from prusa_printer import PrusaPrinter
from google import genai
from google.genai import types as genai_types

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

# Initialize Gemini Client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = None
if GEMINI_API_KEY:
    # Use gemini-3-flash-preview as requested
    client = genai.Client(api_key=GEMINI_API_KEY)

def capture_frame_base64(camera_url):
    import cv2
    if not camera_url:
        return None
        
    cap = cv2.VideoCapture(camera_url)
    if not cap.isOpened():
        return None
    
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        return None
        
    # Encode to JPEG
    _, buffer = cv2.imencode('.jpg', frame)
    return base64.b64encode(buffer).decode('utf-8')


DASHBOARD_URI = "ui://printer-dashboard.html"
SNAPSHOT_URI = "ui://printer-snapshot.html"
ANALYSIS_URI = "ui://printer-analysis.html"

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

@mcp.resource(
    SNAPSHOT_URI,
    mime_type="text/html;profile=mcp-app",
    meta={"ui": {"csp": {"resourceDomains": ["https://unpkg.com", "https://fonts.googleapis.com", "https://fonts.gstatic.com"]}}},
)
def printer_snapshot() -> str:
    """Snapshot HTML resource."""
    snapshot_path = os.path.join(os.path.dirname(__file__), "resources/printer-snapshot.html")
    try:
        with open(snapshot_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<html><body><h1>Error: printer-snapshot.html not found</h1></body></html>"

@mcp.resource(
    ANALYSIS_URI,
    mime_type="text/html;profile=mcp-app",
    meta={"ui": {"csp": {"resourceDomains": ["https://unpkg.com", "https://fonts.googleapis.com", "https://fonts.gstatic.com"]}}},
)
def printer_analysis() -> str:
    """Analysis UI resource."""
    analysis_path = os.path.join(os.path.dirname(__file__), "resources/printer-analysis.html")
    try:
        with open(analysis_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<html><body><h1>Error: printer-analysis.html not found</h1></body></html>"

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

@mcp.tool(meta={
    "ui": {
        "resourceUri": SNAPSHOT_URI
    }
})
async def get_camera_frame() -> list[types.ImageContent | types.TextContent]:
    """
    Take a screenshot from the printer camera (RTSP stream).
    """
    camera_url = os.getenv("CAMERA_URL")
    if not camera_url:
        return [types.TextContent(type="text", text="CAMERA_URL environment variable not set.")]
    
    def capture():
        import cv2
        cap = cv2.VideoCapture(camera_url)
        if not cap.isOpened():
            return None
        
        # Read a few frames to let auto-exposure settle if needed, or just one
        # For RTSP often the first frame is keyframes or might be old buffer, 
        # but for simple screenshot one read is usually usually okay-ish, or we might want to read a couple.
        # Let's just read one for speed.
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return None
            
        # Encode to JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        return  base64.b64encode(buffer).decode('utf-8')

    try:
        # Run blocking cv2/IO in a separate thread
        image_base64 = await asyncio.to_thread(capture_frame_base64, camera_url)
        
        if not image_base64:
             return [types.TextContent(type="text", text="Failed to capture image from camera.")]

        return [types.ImageContent(type="image", data=image_base64, mimeType="image/jpeg")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error capturing image: {str(e)}")]

@mcp.tool(meta={
    "ui": {
        "resourceUri": ANALYSIS_URI
    }
})
async def analyze_print_failure() -> list[types.TextContent | types.ImageContent]:
    """
    Analyze the current printer camera frame for failures (spaghetti, layer shift, etc.) using Gemini.
    """
    if not client:
        return [types.TextContent(type="text", text=json.dumps({"error": "Gemini API key not configured"}))]

    camera_url = os.getenv("CAMERA_URL")
    if not camera_url:
        return [types.TextContent(type="text", text=json.dumps({"error": "CAMERA_URL not set"}))]

    # Capture image
    image_base64 = await asyncio.to_thread(capture_frame_base64, camera_url)
    if not image_base64:
        return [types.TextContent(type="text", text=json.dumps({"error": "Failed to capture image"}))]

    try:
        # Prepare content for Gemini
        image_bytes = base64.b64decode(image_base64)
        
        prompt = """Analyze this 3D printer webcam frame. Detect any print failures:

        Look for:
        - Spaghetti (filament not adhering, creating tangled mess)
        - Layer shifts (horizontal displacement between layers)
        - Warping (corners lifting from bed)
        - Stringing (thin wisps between parts)
        - Bed adhesion failure (part detached from bed)
        - Nozzle blob (material stuck to nozzle)

        Respond in JSON:
        {
            "status": "ok" | "warning" | "failure",
            "issues": [{"type": "...", "confidence": 0.0-1.0, "description": "..."}],
            "recommendation": "continue" | "pause" | "stop"
        }"""

        response = await client.aio.models.generate_content(
            model='gemini-3-flash-preview',
            contents=[
                genai_types.Part(
                    inline_data=genai_types.Blob(
                        mime_type="image/jpeg",
                        data=image_bytes
                    ),
                    media_resolution={"level": "MEDIA_RESOLUTION_MEDIUM"}
                ),
                prompt
            ],
            config={
                'response_mime_type': "application/json",
                'thinking_config': {'include_thoughts': False, 'thinking_level': "LOW"}
            }
        )
        
        # Return both the image (so UI can show what was analyzed) and the text result
        return [
            types.ImageContent(type="image", data=image_base64, mimeType="image/jpeg"),
            types.TextContent(type="text", text=response.text, mimeType="application/json")
        ]
    except Exception as e:
         return [types.TextContent(type="text", text=json.dumps({"error": f"Analysis failed: {str(e)}"}))]


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
