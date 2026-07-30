from dataclasses import dataclass

from langchain.tools import tool, ToolRuntime

from shared.database import get_connection
from shared.validation import customer_exists


@dataclass
class AgentContext:
    user_id: int


@tool(
    "get_customer_profile",
    return_direct=False,
    description="Get the customer profile based on the provided customer ID.",
)
def GetCustomerProfile(runtime: ToolRuntime[AgentContext]) -> dict:

    customer_exists(runtime.context.user_id)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM Customers
        WHERE customer_id = %s
    """, (runtime.context.user_id,))

    customer = cursor.fetchone()

    cursor.close()
    conn.close()

    return customer


@tool(
    "get_booking_history",
    return_direct=False,
    description="Get the booking history for the current customer."
)
def GetBookingHistory(runtime: ToolRuntime[AgentContext]) -> list:

    customer_exists(runtime.context.user_id)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM Bookings
        WHERE customer_id = %s
    """, (runtime.context.user_id,))

    bookings = cursor.fetchall()

    cursor.close()
    conn.close()

    return bookings


@tool(
    "update_customer_profile",
    return_direct=False,
    description="Update the customer profile."
)
def UpdateCustomerProfile(
    runtime: ToolRuntime[AgentContext],
    first_name: str,
    last_name: str,
    email: str,
    phone: str,
) -> dict:

    customer_exists(runtime.context.user_id)

    if not first_name.strip():
        raise ValueError("First name is required.")

    if not last_name.strip():
        raise ValueError("Last name is required.")

    if not email.strip():
        raise ValueError("Email is required.")

    if not phone.strip():
        raise ValueError("Phone number is required.")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Customers
        SET
            first_name=%s,
            last_name=%s,
            email=%s,
            phone=%s
        WHERE customer_id=%s
    """, (
        first_name,
        last_name,
        email,
        phone,
        runtime.context.user_id,
    ))

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "customer_id": runtime.context.user_id,
        "status": "Profile Updated",
    }
