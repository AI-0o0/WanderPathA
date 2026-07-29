import asyncio
import os
import sys
from langchain_mcp_adapters.client import MultiServerMCPClient

# Point to MCP server script relative to this file
path_to_mcp_server = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../server/server.py")
)
mode = sys.argv[1]
async def main():
    # Configure the client connection
    if mode == "stdio":
        server_params = {
            "my_server": {
                "transport": "stdio",
                "command": "python",
                "args": [path_to_mcp_server, "stdio"],
            }
        }
    else:
        server_params = {
            "my_server": {
                "transport": "streamable_http",
                "url": "http://127.0.0.1:8000/mcp",
            }
        }   

    # Initialize the client directly without 'async with'
    client = MultiServerMCPClient(server_params)
    tools = await client.get_tools()
    print("Available tools:", tools)

if __name__ == "__main__":
    asyncio.run(main())