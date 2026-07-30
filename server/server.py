import sys
from fastmcp import FastMCP

# Initialize FastMCP server for WanderPathA
mcp = FastMCP("WanderPathA Travel Agent Server")


if __name__ == "__main__":
    transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"
    if transport == "stdio":
        print("Starting WanderPathA Server [stdio]...")
        mcp.run(transport="stdio")
    elif transport == "http":
        print("Starting WanderPathA Server [http:8000]...")
        mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)