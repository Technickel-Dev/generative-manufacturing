import pytest
from unittest.mock import AsyncMock, patch
from server import get_printer_info, get_printer_status

@pytest.fixture
def mock_printer_api():
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        yield mock_get

@pytest.mark.asyncio
async def test_get_printer_info(mock_printer_api):
    """Test the get_printer_info tool returns the expected format."""
    # Mock responses for info, version, and status
    # get_info() call order: 
    # 1. /api/v1/info -> returns serial/hostname
    # 2. /api/version -> returns firmware/model text
    # 3. /api/v1/status -> returns printer state
    mock_printer_api.side_effect = [
        AsyncMock(status_code=200, json=lambda: {"serial": "CZPX123456789", "hostname": "prusa-mk4"}),
        AsyncMock(status_code=200, json=lambda: {"text": "PrusaLink", "server": "5.1.0"}),
        AsyncMock(status_code=200, json=lambda: {"printer": {"state": "Operational"}})
    ]
    
    result = await get_printer_info.run(arguments={})
    output = result.content[0].text
    assert "Printer: prusa-mk4 (PrusaLink)" in output
    assert "Serial: CZPX123456789" in output
    assert "Firmware: 5.1.0" in output
    assert "State: Operational" in output

@pytest.mark.asyncio
async def test_get_printer_status(mock_printer_api):
    """Test the get_printer_status tool returns the expected format."""
    # Mock responses for status and job
    mock_printer_api.side_effect = [
        AsyncMock(status_code=200, json=lambda: {
            "printer": {
                "state": "Printing",
                "temp_nozzle": 215.5,
                "temp_bed": 60.0,
                "target_nozzle": 215.0,
                "target_bed": 60.0,
                "fan_hotend": 100
            }
        }),
        AsyncMock(status_code=200, json=lambda: {
            "progress": 45.5,
            "time_remaining": 2700,
            "time_printing": 5025
        })
    ]
    
    result = await get_printer_status.run(arguments={})
    output = result.content[0].text
    assert "State: Printing" in output
    assert "Nozzle: 215.5°C" in output
    assert "Progress: 45.5%" in output

