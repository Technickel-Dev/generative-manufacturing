import pytest
import os
from dotenv import load_dotenv
from server import get_printer_info, get_printer_status


# Load environment variables
load_dotenv()

# Check if we have credentials to run live tests
HAS_CREDS = os.getenv("PRINTER_IP") and os.getenv("PRINTER_API_KEY")

@pytest.mark.skipif(not HAS_CREDS, reason="Skipping live tests: No credentials found in .env")
@pytest.mark.asyncio
async def test_live_get_printer_info():
    """Live test: Call get_printer_info against real printer."""
    print(f"\nConnecting to {os.getenv('PRINTER_IP')}...")
    
    # We use the tool directly, which uses the global 'printer' instance in server.py
    # This instance should be initialized with env vars if they exist.
    output = await get_printer_info()
    
    print(f"Result: {output}")
    assert "Printer:" in output

    assert "State:" in output

@pytest.mark.skipif(not HAS_CREDS, reason="Skipping live tests: No credentials found in .env")
@pytest.mark.asyncio
async def test_live_get_printer_status():
    """Live test: Call get_printer_status against real printer."""
    output = await get_printer_status()
    
    print(f"Result: {output}")
    assert "State:" in output
    assert "Nozzle:" in output
    assert "Bed:" in output
