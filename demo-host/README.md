# Generative Manufacturing Demo Host

A reference implementation showing how to build an MCP host application that connects to MCP servers and renders tool UIs in a secure sandbox. This host is specifically configured to demonstrate the Generative Manufacturing MCP server.

## Prerequisites

- **Node.js** (v18 or higher)
- **npm** (v9 or higher)

## Getting Started

1.  **Navigate to this directory**:
    ```bash
    cd demo-host
    ```

2.  **Install dependencies**:
    ```bash
    npm install
    ```

3.  **Start the development server**:
    ```bash
    npm run start
    ```

4.  **Open the application**:
    Navigate to [http://localhost:8080](http://localhost:8080) in your browser.

## Configuration

By default, the host application will try to connect to an MCP server at `http://localhost:3001/mcp`.

You can configure this behavior by setting the `SERVERS` environment variable with a JSON array of server URLs:

```bash
SERVERS='["http://localhost:1234/mcp", "http://localhost:5678/mcp"]' npm run start
```

## Architecture

This example uses a double-iframe sandbox pattern for secure UI isolation:

```
Host (port 8080)
  └── Outer iframe (port 8081) - sandbox proxy
        └── Inner iframe (srcdoc) - untrusted tool UI
```

**Why two iframes?**

- The outer iframe runs on a separate origin (port 8081) preventing direct access to the host
- The inner iframe receives HTML via `srcdoc` and is restricted by sandbox attributes
- Messages flow through the outer iframe which validates and relays them bidirectionally

This architecture ensures that even if tool UI code is malicious, it cannot access the host application's DOM, cookies, or JavaScript context.

## Attribution

This host is based on the [basic-host example](https://github.com/modelcontextprotocol/ext-apps) provided by the Model Context Protocol team, licensed under Apache 2.0 / MIT.
