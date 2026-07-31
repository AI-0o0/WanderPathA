import asyncio
import os
import sys

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.resources import load_mcp_resources
from langchain_mcp_adapters.callbacks import Callbacks, CallbackContext

path_to_mcp_server = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../server/server.py")
)

mode = sys.argv[1] if len(sys.argv) > 1 else "stdio"

from mcp.types import ElicitResult

async def on_elicitation(
    mcp_context,
    params,
    context,
):
    print("\n" + "=" * 50)
    print("REFUND CONFIRMATION")
    print("=" * 50)

    print(params.message)

    answer = input("\nType 'confirm' or 'cancel': ").strip().lower()

    if answer == "confirm":
        return ElicitResult(
            action="accept",
            content={
                "value": "confirm"
            }
        )

    return ElicitResult(
        action="decline",
    )
callbacks = Callbacks(
    on_elicitation=on_elicitation
)



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
        raise ValueError(f"Invalid mode: {mode}. Must be 'stdio' or 'http'.")
    print(f"\nConnecting using [{mode}] transport...\n")
    client = MultiServerMCPClient(
    server_params,
    callbacks=callbacks,
    )
    async with client.session("wanderpath_server") as session:
        # 1. Capability Negotiation
        caps = session.get_server_capabilities()
        print("=" * 60)
        print("CAPABILITY NEGOTIATION")
        print("=" * 60)
        print(f"Tools Supported      : {caps.tools is not None}")
        print(f"Resources Supported  : {caps.resources is not None}")
        print(f"Prompts Supported    : {caps.prompts is not None}")
        print("=" * 60)
        # 2. Resource Discovery
        if caps.resources is not None:
            print("\nRESOURCE DISCOVERY")
            resources = await load_mcp_resources(session)
            if resources:
                print(f"Found {len(resources)} resource(s)\n")
            for resource in resources:
                metadata = getattr(resource, "metadata", {})
                uri = metadata.get("uri", "Unknown URI")

                print(f"  URI : {uri}")
                print(f"  Data: {resource.data}")
            if len(resources) == 0:
                print("Server supports resources, but none are registered.")
        # 3. Prompt Discovery
        if caps.prompts is not None:
            print("\nPROMPT DISCOVERY")
            result = await session.list_prompts()
            prompts = getattr(result, "prompts", [])
            if prompts:
                print(f"Found {len(prompts)} prompt(s)\n")
                for prompt in prompts:
                    print(f"- {prompt.name}")
            else:
                print("Server supports prompts, but none are registered.")

        # 4. Tool Discovery
        if caps.tools is not None:
            print("\nTOOL DISCOVERY")
            tools = await load_mcp_tools(session)
            if tools:
                print(f"Found {len(tools)} tool(s)\n")
                for tool in tools:
                    print(f"- {tool.name}")
                    if tool.description:
                        print(f"  {tool.description}")
            else:
                print("Server supports tools, but no tools are registered.")

        print("\nFinished.")
        return client


if __name__ == "__main__":
    asyncio.run(create_client())