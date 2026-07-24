import json
from pathlib import Path
from langchain.tools import tool

DATA_DIR = Path(__file__).resolve().parent.parent / "shared" / "data"


@tool(
    "get_nearby_airports",
    return_direct=False,
    description="Get nearby airports based on the provided city.",
)
def GetNearbyAirports(city: str) -> list:
    """
    Get all airports located in the specified city.
    """
    with open(DATA_DIR / "airports.json", "r", encoding="utf-8") as file:
        airports = json.load(file)

    city = city.strip().lower()

    return [
        {
            "skyId": code,
            **airport,
        }
        for code, airport in airports.items()
        if airport["city"].strip().lower() == city
    ]


@tool(
    "get_flight_options",
    return_direct=False,
    description="Get flight options based on the provided parameters.",
)
def GetFlightOptions(
    originSkyId: str,
    destinationSkyId: str,
    departureDate: str,
) -> list:
    """
    Get flight options based on the provided parameters.

    Args:
        originSkyId: Origin airport code (e.g. CAI).
        destinationSkyId: Destination airport code (e.g. DXB).
        departureDate: Departure date in YYYY-MM-DD format.

    Returns:
        A list of matching flights.
    """
    with open(DATA_DIR / "flights.json", "r", encoding="utf-8") as file:
        flights = json.load(file)

    return [
        {
            "flight_id": flight_id,
            **flight,
        }
        for flight_id, flight in flights.items()
        if (
            flight["origin"] == originSkyId
            and flight["destination"] == destinationSkyId
            and flight["departure_date"] == departureDate
        )
    ]