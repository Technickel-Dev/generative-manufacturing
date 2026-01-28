# License & Attribution

The core logic of this system (located in generative-manufacturing-server) is original work licensed under the MIT License.

The demo infrastructure (located in demo-host) is based on the basic-hostexample provided in [MCP Apps Extension (SEP-1865)](https://github.com/modelcontextprotocol/ext-apps) and is included under the Apache 2.0 / MIT License. We have extended this MCP host by modifying to use our MCP server to demonstrate generative manufacturing. We have also modified the look of the tool and for the host to be able to run independently deployed for users to try and see the demo.

The backend utilizes OpenSCAD (GPLv2) for 3D generation. OpenSCAD is installed unmodified as a standalone utility and is executed via command-line interface.

The backend utilizes PrusaSlicer (AGPLv3) for 3D printing slicing. PrusaSlicer is installed unmodified as a standalone utility and is executed via command-line interface.