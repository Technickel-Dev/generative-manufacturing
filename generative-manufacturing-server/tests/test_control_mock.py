import pytest
from unittest.mock import AsyncMock, patch
from server import pause_printer, resume_printer, stop_printer

@pytest.mark.asyncio
async def test_pause_printer(mocker):
    # Mock the printer object in server.py
    # Since server.py initializes 'printer' globally, we can mock 'httpx.AsyncClient' 
    # used inside PrusaPrinter methods OR mock the 'printer' object itself.
    # Let's mock the httpx client to verify the actual calls made by PrusaPrinter.
    
    mock_post = mocker.patch("httpx.AsyncClient.post", new_callable=AsyncMock)
    mock_post.return_value.status_code = 204
    
    result = await pause_printer()
    
    assert "Success" in result
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert "/api/v1/job" in args[0]
    assert kwargs['json'] == {"command": "pause"}

@pytest.mark.asyncio
async def test_resume_printer(mocker):
    mock_post = mocker.patch("httpx.AsyncClient.post", new_callable=AsyncMock)
    mock_post.return_value.status_code = 204
    
    result = await resume_printer()
    
    assert "Success" in result
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert "/api/v1/job" in args[0]
    assert kwargs['json'] == {"command": "resume"}

@pytest.mark.asyncio
async def test_stop_printer(mocker):
    mock_delete = mocker.patch("httpx.AsyncClient.delete", new_callable=AsyncMock)
    mock_delete.return_value.status_code = 204
    
    result = await stop_printer()
    
    assert "Success" in result
    mock_delete.assert_called_once()
    args, _ = mock_delete.call_args
    assert "/api/v1/job" in args[0]
