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
import glob
from slicer_runner import SlicerRunner

# Load environment variables
load_dotenv()

# Initialize Printer Client
PRINTER_IP = os.getenv("PRINTER_IP", "127.0.0.1")
PRINTER_API_KEY = os.getenv("PRINTER_API_KEY", "dummy_key")

printer = PrusaPrinter(ip=PRINTER_IP, api_key=PRINTER_API_KEY)
slicer = SlicerRunner()
MODELS_DIR = os.path.join(os.path.dirname(__file__), "assets/models")
if not os.path.exists(MODELS_DIR):
    os.makedirs(MODELS_DIR)

# Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "3001"))

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

def capture_frame_base64(camera_url, quality=80):
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
        
    # Resize to reduce size (standardize to VGA for analysis)
    # This ensures consistency and lower token usage
    resized_frame = cv2.resize(frame, (640, 480), interpolation=cv2.INTER_AREA)
        
    # Encode to JPEG with specified quality
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    _, buffer = cv2.imencode('.jpg', resized_frame, encode_param)
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
async def pause_printer() -> str:
    """
    Pause the current print job.
    """
    try:
        result = await printer.pause_print()
        return f"Success: {result.get('message', 'Print paused')}"
    except Exception as e:
        return f"Error pausing printer: {str(e)}"

@mcp.tool()
async def resume_printer() -> str:
    """
    Resume the current print job.
    """
    try:
        result = await printer.resume_print()
        return f"Success: {result.get('message', 'Print resumed')}"
    except Exception as e:
        return f"Error resuming printer: {str(e)}"

@mcp.tool()
async def stop_printer() -> str:
    """
    Stop (Cancel) the current print job. WARNING: This cannot be undone.
    """
    try:
        result = await printer.stop_print()
        return f"Success: {result.get('message', 'Print stopped')}"
    except Exception as e:
        return f"Error stopping printer: {str(e)}"

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

async def get_printer_status_for_gemini():
    """
    Get the current status of the printer including temperatures, progress, and state.
    Use this to check if the printer is active, paused, or finished, and to verify temperatures.
    """
    try:
        return await printer.get_status()
    except Exception as e:
        return {"error": f"Failed to get status: {str(e)}"}

async def _analyze_with_gemini(image_base64: str, thinking_level: str, tools=None, prompt=None, media_resolution="MEDIA_RESOLUTION_MEDIUM") -> list[types.TextContent | types.ImageContent]:
    """
    Helper function to perform analysis using Gemini with specified thinking level and tools.
    Handles multi-turn function calling interactions.
    """
    if not client:
        return [types.TextContent(type="text", text=json.dumps({"error": "Gemini API key not configured"}))]

    try:
        # Prepare content for Gemini
        image_bytes = base64.b64decode(image_base64)
        
        if not prompt:
            prompt = """Analyze this 3D printer webcam frame. Detect any print failures.
        
        If you are unsure about the printer's state (e.g., if it looks paused or finished), USE THE AVAILABLE TOOLS to check the printer status.

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

        config = {
            'response_mime_type': "application/json",
            'thinking_config': {'include_thoughts': False, 'thinking_level': thinking_level}
        }
        
        # Tool configuration - pass inside config
        if tools:
            config['tools'] = tools

        # Build initial contents
        contents = [
            genai_types.Part(
                inline_data=genai_types.Blob(
                    mime_type="image/jpeg",
                    data=image_bytes
                ),
                media_resolution={"level": media_resolution}
            ),
            genai_types.Part(text=prompt)
        ]

        MAX_TURNS = 5
        current_turn = 0
        
        while current_turn < MAX_TURNS:
            response = await client.aio.models.generate_content(
                model='gemini-3-flash-preview',
                contents=contents,
                config=config
            )

            # Check for function calls
            # The structure of `response` depends on the SDK, but typically we check candidates[0].content.parts
            # Using the simplified check provided by the SDK usually available on `response`.
            
            function_calls = []
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if part.function_call:
                        function_calls.append(part.function_call)

            if not function_calls:
                # No function calls, this is the final response
                return [
                    types.ImageContent(type="image", data=image_base64, mimeType="image/jpeg"),
                    types.TextContent(type="text", text=response.text, mimeType="application/json")
                ]
            
            # If we have function calls, execute them
            # Append the model's response (with function calls) to history
            contents.append(response.candidates[0].content)
            
            for fc in function_calls:
                func_name = fc.name
                func_args = fc.args
                
                # Execute valid tools
                function_result = None
                if func_name == "get_printer_status_for_gemini":
                    result_data = await get_printer_status_for_gemini()
                    function_result = json.dumps(result_data)
                else:
                    function_result = json.dumps({"error": f"Unknown function {func_name}"})
                
                # Append function response to history
                contents.append(genai_types.Content(
                    role="user",
                    parts=[genai_types.Part(
                        function_response=genai_types.FunctionResponse(
                            name=func_name,
                            response={"result": function_result} 
                        )
                    )]
                ))
            
            current_turn += 1

        return [types.TextContent(type="text", text=json.dumps({"error": "Analysis failed: Too many tool turns."}))]

    except Exception as e:
         return [types.TextContent(type="text", text=json.dumps({"error": f"Analysis failed: {str(e)}"}))]


@mcp.tool(meta={
    "ui": {
        "resourceUri": ANALYSIS_URI
    }
})
async def quick_print_check() -> list[types.TextContent | types.ImageContent]:
    """
    Perform a quick status check of the print. 
    Uses LOW thinking level for low latency. 
    Can check printer status if visual info is ambiguous.
    """
    camera_url = os.getenv("CAMERA_URL")
    if not camera_url:
        return [types.TextContent(type="text", text=json.dumps({"error": "CAMERA_URL not set"}))]

    # Capture image with 50% quality
    image_base64 = await asyncio.to_thread(capture_frame_base64, camera_url, quality=50)
    if not image_base64:
        return [types.TextContent(type="text", text=json.dumps({"error": "Failed to capture image"}))]

    # Use LOW thinking and provide status tool
    prompt = """Analyze this 3D printer webcam frame. Perform a quick status check.
    If visual info is ambiguous, use tools to check printer status.
    Respond in JSON:
    {
        "status": "ok" | "warning" | "failure",
        "recommendation": "continue" | "pause" | "stop"
    }
    Do NOT list specific issues. Keep the response minimal."""
    
    return await _analyze_with_gemini(image_base64, thinking_level="LOW", tools=[get_printer_status_for_gemini], prompt=prompt, media_resolution="MEDIA_RESOLUTION_LOW")


@mcp.tool(meta={
    "ui": {
        "resourceUri": ANALYSIS_URI
    }
})
async def deep_print_check() -> list[types.TextContent | types.ImageContent]:
    """
    Perform a deep, complex diagnosis of a potential failure.
    Uses HIGH thinking level for reasoning.
    """
    camera_url = os.getenv("CAMERA_URL")
    if not camera_url:
        return [types.TextContent(type="text", text=json.dumps({"error": "CAMERA_URL not set"}))]

    # Capture image with higher quality (80%) for deep analysis
    image_base64 = await asyncio.to_thread(capture_frame_base64, camera_url, quality=80)
    if not image_base64:
        return [types.TextContent(type="text", text=json.dumps({"error": "Failed to capture image"}))]

    # Use HIGH thinking
    return await _analyze_with_gemini(image_base64, thinking_level="HIGH", media_resolution="MEDIA_RESOLUTION_HIGH")

INCIDENT_URI = "ui://printer-incident.html"

@mcp.resource(
    INCIDENT_URI,
    mime_type="text/html;profile=mcp-app",
    meta={"ui": {"csp": {"resourceDomains": ["https://unpkg.com", "https://fonts.googleapis.com", "https://fonts.gstatic.com"]}}},
)
def printer_incident() -> str:
    """Incident Dashboard HTML resource."""
    path = os.path.join(os.path.dirname(__file__), "resources/printer-incident.html")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<html><body><h1>Error: printer-incident.html not found</h1></body></html>"

@mcp.tool(meta={
    "ui": {
        "resourceUri": INCIDENT_URI
    }
})
async def simulate_spaghetti_incident() -> list[types.TextContent]:
    """
    Simulate a spaghetti failure incident for testing the UI.
    """
    fake_analysis = {
        "status": "failure",
        "issues": [
            {"type": "Spaghetti", "confidence": 0.95, "description": "Severe filament tangling detected on build plate."}
        ],
        "recommendation": "stop"
    }
    # 1x1 Black Pixel JPEG
    fake_image = "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEGMgASIAAhEBEQA/8QAFgABAQEAAAAAAAAAAAAAAAAAAwQFAAEBAQEAAAAAAAAAAAAAAAAAAQACEAACAQIDEAAAAAAAAAAAAAAAAJEQITFBEhEAAgIBAwUAAAAAAAAAAAAAAREhADFBUWGRof/aAAwDAQACEQMRAD8AQ0s1U1f/2Q=="
    
    return await review_latest_incident(fake_analysis, fake_image)

@mcp.tool(meta={
    "ui": {
        "resourceUri": INCIDENT_URI
    }
})
async def review_latest_incident(analysis: dict | str, image: str | None = None) -> list[types.TextContent]:
    """
    Review a detected incident.
    Returns the analysis report, snapshot, and relevant SOPs.
    
    Args:
        analysis: Analysis result object or JSON string (status, issues, etc.)
        image: Optional base64 encoded image string
    """
    import glob
    
    analysis_data = analysis
    if isinstance(analysis, str):
        try:
            analysis_data = json.loads(analysis)
        except json.JSONDecodeError:
            return [types.TextContent(type="text", text=json.dumps({
                "error": "Invalid analysis JSON provided.",
                "analysis": None,
                "sops": []
            }))]
    
    # Find relevant SOPs
    sops = []
    sop_dir = os.path.join(os.path.dirname(__file__), "assets/sop")
    
    # Always include Safety SOP
    safety_path = os.path.join(sop_dir, "safety.md")
    # Match issues to SOPs
    if analysis_data.get("issues"):
        for issue in analysis_data["issues"]:
            issue_type = issue.get("type", "").lower()
            # Simple keyword matching against filenames
            for sop_file in glob.glob(os.path.join(sop_dir, "*.md")):
                filename = os.path.basename(sop_file).lower()
                clean_name = filename.replace(".md", "").replace("_", " ")
                
                # Check for match (either direction)
                if (clean_name in issue_type) or (issue_type in clean_name):
                    # Avoid duplicates
                    if not any(s["title"] == clean_name.title() for s in sops):
                        with open(sop_file, "r", encoding="utf-8") as f:
                            sops.append({
                                "title": clean_name.replace("_", " ").title(),
                                "content": f.read()
                            })

    # Always include Safety SOP at the end
    safety_path = os.path.join(sop_dir, "safety.md")
    if os.path.exists(safety_path):
        with open(safety_path, "r", encoding="utf-8") as f:
            sops.append({"title": "Safety Protocols", "content": f.read()})

    # Construct response
    result = {
        "analysis": analysis_data,
        "image": image,
        "sops": sops
    }
    
    
    return [types.TextContent(type="text", text=json.dumps(result), mimeType="application/json")]

@mcp.tool()
async def list_local_models() -> str:
    """List available STL files in the local models directory."""
    try:
        files = glob.glob(os.path.join(MODELS_DIR, "*.stl"))
        if not files:
            return "No STL files found in models directory."
        
        return "Available models:\n" + "\n".join([os.path.basename(f) for f in files])
    except Exception as e:
        return f"Error listing models: {str(e)}"

@mcp.tool()
async def slice_model(model_filename: str, intent: str = "default") -> str:
    """
    Slice a 3D model (STL) into G-code with specific settings based on intent.
    Intent examples: 'draft', 'fast', 'strong', 'detail'.
    """
    try:
        input_path = os.path.join(MODELS_DIR, model_filename)
        output_filename = model_filename.lower().replace(".stl", ".gcode")
        output_path = os.path.join(MODELS_DIR, output_filename)
        
        # Run slicing in a separate thread to avoid blocking the event loop
        result = await asyncio.to_thread(slicer.slice_file, input_path, output_path, intent)
        
        if result["success"]:
            return f"Successfully sliced {model_filename} to {output_filename}.\nMessage: {result['message']}"
        else:
            return f"Slicing failed: {result['error']}"
    except Exception as e:
        return f"Error executing slice: {str(e)}"

@mcp.tool()
async def upload_model(gcode_filename: str) -> str:
    """
    Upload a G-code file from the local models directory to the printer.
    """
    try:
        file_path = os.path.join(MODELS_DIR, gcode_filename)
        result = await printer.upload_file(file_path)
        return f"Upload result: {result.get('message', 'Unknown status')}"
    except Exception as e:
        return f"Error uploading file: {str(e)}"


if __name__ == "__main__":
    app = mcp.streamable_http_app(stateless_http=True)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    print(f"Generative Manufacturing Server listening on http://{HOST}:{PORT}/mcp")
    uvicorn.run(app, host=HOST, port=PORT)
