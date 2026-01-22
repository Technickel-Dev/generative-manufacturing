from fastmcp import FastMCP
from printer import PrusaPrinter
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastMCP Server
mcp = FastMCP("Generative Manufacturing")

# Initialize Printer Client
# In a real scenario, we'd probably want better configuration management
PRINTER_IP = os.getenv("PRINTER_IP", "127.0.0.1")
PRINTER_API_KEY = os.getenv("PRINTER_API_KEY", "dummy_key")

printer = PrusaPrinter(ip=PRINTER_IP, api_key=PRINTER_API_KEY)

@mcp.tool()
async def get_printer_info() -> str:
    """
    Get basic information about the connected Prusa printer (Model, Serial, Firmware).
    """
    try:
        info = await printer.get_info()
        return f"Printer: {info['name']} ({info['model']})\nSerial: {info['serial']}\nFirmware: {info['firmware']}\nState: {info['state']}"
    except Exception as e:
        return f"Error fetching printer info: {str(e)}"

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
                f"Progress: {status['progress']}%\n"
                f"Time Remaining: {status['time_remaining']}")
    except Exception as e:
        return f"Error fetching printer status: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
