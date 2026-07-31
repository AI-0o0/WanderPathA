import asyncio
import os
import sys

from langchain_mcp_adapters.client import MultiServerMCPClient

from agent import run_agent  

path_to_mcp_server = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../server/server.py")
)

mode = sys.argv[1] if len(sys.argv) > 1 else "stdio"


async def create_client():
    if mode == "stdio":
        server_params = {
            "wanderpath_server": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [path_to_mcp_server, "stdio"],
            }
        }

    elif mode == "http":
        server_params = {
            "wanderpath_server": {
                "transport": "http",
                "url": "http://127.0.0.1:8000/mcp",
            }
        }

    else:
        raise ValueError("Mode must be 'stdio' or 'http'.")

    return MultiServerMCPClient(server_params)


async def main():

    client = await create_client()
    tools = await client.get_tools()
    print(f"Loaded MCP Tools: {[t.name for t in tools]}")

    print("===================================")
    print("WanderPath Travel Support Agent")
    print("Type 'exit' to quit")
    print("===================================\n")

    while True:

        user_input = input("User: ").strip()

        if user_input.lower() == "exit":
            break

        await run_agent(
            client=client,
            user_input=user_input,
            user_id="C001"
        )


if __name__ == "__main__":
    asyncio.run(main())