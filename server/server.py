import sys
import os
from fastmcp import FastMCP
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)
from tools.travel_status_tools import (
    get_flight_status,
    get_weather,
    get_delay_duration,
    check_disruption_reason
)
from tools.booking_tools import (
    GetNearbyAirports,
    GetFlightOptions
)

# Initialize FastMCP server for WanderPathA
mcp = FastMCP("WanderPathA Travel Agent Server")

mcp.tool()(get_flight_status.func)
mcp.tool()(get_weather.func)
mcp.tool()(get_delay_duration.func)
mcp.tool()(check_disruption_reason.func)
mcp.tool()(GetNearbyAirports.func)
mcp.tool()(GetFlightOptions.func)

if __name__ == "__main__":
    transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"
    if transport == "stdio":
        sys.stderr.write("Starting WanderPathA Server [stdio]...")
        mcp.run(transport="stdio")
    elif transport == "http":
        sys.stderr.write("Starting WanderPathA Server [http:8000]...")
        mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)