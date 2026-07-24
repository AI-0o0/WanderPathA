import os
from dotenv import load_dotenv

load_dotenv()
X_RAPIDAPI_KEY = os.getenv("X_RAPIDAPI_KEY")

import json
import pycountry
import http.client
from langchain.tools import tool, ToolRuntime

from dataclasses import dataclass

@dataclass
class AgentContext:
    user_id: str

def _country_code(country_name: str, default: str = "") -> str:
    country = pycountry.countries.get(name=country_name)
    if country:
        return country.alpha_2
    return default


def _load_json_file(file_path: str, default):
    try:
        with open(file_path, "r") as f:
            content = f.read().strip()
            if not content:
                return default
            return json.loads(content)
    except FileNotFoundError:
        return default

@tool("get_customer_profile", return_direct=False, description="Get the customer profile based on the provided customer ID.")
def GetCustomerProfile(runtime: ToolRuntime[AgentContext]) -> dict:
    """
    Get the customer profile based on the provided customer ID.
    Args:
        runtime (ToolRuntime[AgentContext]): The runtime context containing the user ID.
    """
    customers = _load_json_file('shared/data/customers.json', {})
    return customers.get(runtime.context.user_id, {})

@tool(
    "get_booking_history",
    return_direct=False,
    description="Get the booking history for the current customer."
)
def GetBookingHistory(runtime: ToolRuntime[AgentContext]) -> list:
    bookings = _load_json_file("shared/data/bookings.json", {})

    return [
        {
            "booking_id": booking_id,
            **booking,
        }
        for booking_id, booking in bookings.items()
        if booking["customer_id"] == runtime.context.user_id
    ]

@tool("update_customer_profile", return_direct=False, description="Update the customer profile based on the provided customer ID and new profile data.")
def UpdateCustomerProfile(runtime: ToolRuntime[AgentContext], new_profile: dict) -> dict:
    """
    Update the customer profile based on the provided customer ID and new profile data.
    Args:
        runtime (ToolRuntime[AgentContext]): The runtime context containing the user ID.
        new_profile: A dictionary containing the new profile data for the customer.
    """
    customers = _load_json_file('shared/data/customers.json', {})
    
    customers[runtime.context.user_id] = new_profile
    
    with open('shared/data/customers.json', 'w') as f:
        json.dump(customers, f, indent=4)
    
    return customers[runtime.context.user_id]