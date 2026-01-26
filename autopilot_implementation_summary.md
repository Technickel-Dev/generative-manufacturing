# Auto-Pilot Implementation Summary

## Overview
This document summarizes the attempt to implement an "Auto-Pilot" feature for the Lights Out Factory. The goal was to create a background service that periodically checks the printer's status using computer vision and automatically pauses the print if failures (like spaghetti or layer shifts) are detected.

## Architectural Approach

### 1. Shared Analysis Logic
We created a dedicated utility to handle interactions with Gemini 3.
- **Purpose**: To ensure consistency between manual checks (triggered by the user) and automated checks (triggered by the Auto-Pilot).
- **Mechanism**: A shared function that accepts an image, sends it to Gemini with specific "failure detection" prompts, and parses the JSON response.

### 2. Monitoring Service (`MonitoringService`)
A background service class designed to run independently of the main server request loop.
- **Lifecycle**: Manages a background `asyncio` task that wakes up every check interval (e.g., 15s).
- **Logic**:
    1.  Checks if the printer is active.
    2.  Captures a frame from the webcam.
    3.  Sends the frame to the shared analysis utility.
    4.  Logs the result to a history list.
    5.  **Intervention**: If a "failure" is detected, it automatically calls the printer's `pause` function.

### 3. Server Integration
The main server was updated to expose this functionality via the Model Context Protocol (MCP).
- **New Tools**:
    - `set_autopilot(enabled)`: To toggle the background service.
    - `get_autopilot_history()`: To retrieve the log of recent checks.
- **Resources**:
    - `autopilot-log`: A JSON resource for the frontend to poll and display the live activity feed.

### 4. Frontend (Dashboard)
We attempted to update the printer dashboard to include:
- A toggle switch for the Auto-Pilot.
- A scrolling "Activity Feed" showing the results of the periodic checks (e.g., "✅ Active", "⚠️ Suspicious").

## Challenges Encountered
- **Connectivity**: Issues were faced with the frontend connecting to the backend service.
- **State Management**: Ensuring the background loop correctly handled the printer's state without blocking the main server threads.

## Recommendations for Next Attempt
- **Simplify**: Start with a simple "one-shot" tool that the user triggers manually to verify the vision pipeline before building the automatic loop.
- **Robust Networking**: Ensure the frontend and backend ports are correctly configured and allowlisted (CORS/CSP) from the start.
- **Logging**: Add more verbose logging to the frontend to debug connection failures immediately.
