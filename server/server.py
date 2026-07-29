import os
from fastmcp import FastMCP
import sys

mcp = FastMCP()

@mcp.tool('test')
def ping():
    return 'pong'

@mcp.tool('add')
def add_numbers(a: int, b: int) -> int:
    return a + b

if __name__ == '__main__':
    transport = sys.argv[1] if len(sys.argv) > 1 else 'stdio'
    if transport == 'stdio':
        print("Starting MCP server with stdio transport...")
        mcp.run(transport='stdio')
    elif transport == 'http':
        print("Starting MCP server with streamable-http transport...")
        mcp.run(transport='streamable-http', host='0.0.0.0', port=8000)
        