import pytest
from mcp.server.fastmcp import FastMCP
from mcp import types
import json
import os
from unittest.mock import MagicMock, patch

# Import the server module (we need to be able to import it)
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import server

@pytest.mark.asyncio
async def test_snapshot_resource_registered():
    """Verify that the snapshot resource is registered correctly."""
    # Check if the resource is in the server's capabilities/resources
    # FastMCP stores resources in an internal list/registry.
    # We can inspect server.mcp._resource_manager._resources or similar
    # But for a cleaner check, we can list resources if enabled, or check the route.
    
    # Check if SNAPSHOT_URI is defined
    assert server.SNAPSHOT_URI == "ui://printer-snapshot.html"
    
    # Verify the resource function exists and reads the file
    result = server.printer_snapshot()
    assert "<!DOCTYPE html>" in result
    assert "Printer Snapshot" in result
    assert 'style="display: none;"' in result  # Check refresh button is hidden
    assert 'app.callServerTool({ name: "get_camera_frame", arguments: {} })' in result  # Check refresh logic

@pytest.mark.asyncio
async def test_get_camera_frame_metadata():
    """Verify that get_camera_frame tool has the correct UI metadata."""
    # Find the tool definition
    tool_name = "get_camera_frame"
    
    # FastMCP wrapper exposes the tool. We need to check how it's registered.
    # In FastMCP, tools are decorators. The function itself might be wrapped.
    # Or we can check server.mcp._tool_manager._tools
    
    tool_def = None
    # Accessing private members for testing verification
    for tool in server.mcp._tool_manager._tools.values():
         if tool.name == tool_name:
             tool_def = tool
             break
    
    assert tool_def is not None
    assert "ui" in tool_def.meta
    assert tool_def.meta["ui"]["resourceUri"] == server.SNAPSHOT_URI
    
