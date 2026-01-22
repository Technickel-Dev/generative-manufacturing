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
    # Mock responses for version and status
    mock_printer_api.side_effect = [
        AsyncMock(status_code=200, json=lambda: {"serial": "CZPX123456789", "firmware": "5.1.0"}),
        AsyncMock(status_code=200, json=lambda: {"printer": {"name": "Prusa MK4", "type": "MK4", "state": "Operational"}})
    ]
    
    result = await get_printer_info.run(arguments={})
    output = result.content[0].text
    assert "Printer: Prusa MK4" in output
    assert "Serial: CZPX123456789" in output

@pytest.mark.asyncio
async def test_get_printer_status(mock_printer_api):
    """Test the get_printer_status tool returns the expected format."""
    # Mock responses for status and job
    mock_printer_api.side_effect = [
        AsyncMock(status_code=200, json=lambda: {
            "printer": {
                "state": "Printing",
                "temp": {"nozzle": 215.5, "bed": 60.0},
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

