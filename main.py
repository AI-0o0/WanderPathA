import asyncio
import os
import sys

from langchain_mcp_adapters.client import MultiServerMCPClient


from agent import run_agent  
from client import create_client

path_to_mcp_server = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../server/server.py")
)

mode = sys.argv[1] if len(sys.argv) > 1 else "stdio"

async def main():

    client = await create_client()
    tools = await client.get_tools()

    print("===================================")
    print("WanderPath Travel Support Agent")
    print("Type 'exit' to quit")
    print("===================================\n")

    logged_in = True
    while True:
        user_id = input("Enter your user ID login: ").strip() # temp for testing
        logged_in = True
        if user_id.lower() == "exit":
                break
        while logged_in == True:

            user_input = input("User: ").strip()


            if user_input.lower() == "logout":
                logged_in = False
                print("Logged out.")
                break

            await run_agent(
                client=client,
                user_input=user_input,
                user_id=user_id
            )


if __name__ == "__main__":
    asyncio.run(main())