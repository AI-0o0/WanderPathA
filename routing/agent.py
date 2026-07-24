from dataclasses import dataclass
from typing import Literal

from dotenv import load_dotenv

from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

from tools.customer_tools import GetBookingHistory
from tools.travel_status_tools import (
    get_flight_status,
    get_delay_duration,
    check_connection_risk,
    check_alternative_transport,
)
from tools.finance_and_decision_tools import (
    CheckRefundEligibility,
    CalculateRefundAmount,
    ProcessRefund,
)
from tools.escalation_tools import (
    escalate_to_human,
)

load_dotenv()


@dataclass
class AgentContext:
    user_id: str


@dataclass
class ToolRuntimeShim:
    context: AgentContext


class RouteDecision(BaseModel):
    category: Literal[
        "Refund",
        "Rebooking",
        "Flight Information",
        "Escalation",
    ]


SYSTEM_PROMPT = """
You are a Travel Support Routing Agent.

Your job is ONLY to classify the customer's request into ONE category.

Available categories:

- Refund
- Rebooking
- Flight Information
- Escalation

Guidelines:

Refund:
- refund
- money back
- reimbursement
- compensation
- travel voucher

Rebooking:
- delayed flight
- cancelled flight
- another flight
- missed connection
- change booking

Flight Information:
- flight status
- delay
- departure
- arrival
- airport information

Escalation:
- complaint
- supervisor
- manager
- human support
- legal issue

Return ONLY the structured output.

Never answer the customer.
"""


router = (
    init_chat_model(
        model="google_genai:gemini-3.5-flash-lite",
        max_tokens=256,
        max_retries=3,
    )
    .with_structured_output(RouteDecision)
)


def run_agent(user_id: str = "C001"):

    print("Welcome to the Routing Travel Support Agent!")

    context = AgentContext(user_id=user_id)

    messages = [
        SystemMessage(content=SYSTEM_PROMPT)
    ]

    while True:

        user_input = input("User: ").strip()

        if not user_input:
            continue

        messages.append(
            HumanMessage(content=user_input)
        )

        route = router.invoke(messages)
        if route.category != "Escalation":

            booking_history = GetBookingHistory.func(
                ToolRuntimeShim(context=context)
            )

            if not booking_history:
                print("Agent: No booking found for this customer.")
                continue

            booking = booking_history[0]
            booking_id = booking["booking_id"]
            flight_id = booking["flight_id"]

        if route.category == "Refund":

            eligible = CheckRefundEligibility.invoke(
                {"booking_id": booking_id}
            )

            if not eligible:
                print("Agent: Your booking is not eligible for a refund.")
                continue

            refund_amount = CalculateRefundAmount.invoke(
                {"booking_id": booking_id}
            )

            ProcessRefund.invoke(
                {"booking_id": booking_id}
            )

            print(
                "Agent: Refund processed successfully."
            )
            print(
                f"Refund Amount: ${refund_amount}"
            )

        elif route.category == "Flight Information":

            status = get_flight_status.invoke(
                {
                    "flight_id": flight_id
                }
            )

            delay = get_delay_duration.invoke(
                {
                    "flight_id": flight_id
                }
            )

            connection_risk = check_connection_risk.invoke(
                {
                    "flight_id": flight_id
                }
            )

            print("\nFlight Information")
            print("-------------------------")
            print(f"Flight ID: {flight_id}")
            print(f"Status: {status}")
            print(f"Delay: {delay} minutes")
            print(f"Connection Risk: {connection_risk}")

        elif route.category == "Rebooking":

            delay = get_delay_duration.invoke(
                {
                    "flight_id": flight_id
                }
            )

            status = get_flight_status.invoke(
                {
                    "flight_id": flight_id
                }
            )

            if status.lower() != "cancelled" and delay < 180:

                print(
                    "Agent: Your flight does not currently require rebooking."
                )

                continue

            #
            # Current demo data contains one booking:
            # MS101 -> DXB
            #
            alternatives = check_alternative_transport.invoke(
                {
                    "destination": "DXB"
                }
            )

            if alternatives:

                print("\nAgent: Available Alternatives")

                for option in alternatives:

                    if "flight_number" in option:

                        print(
                            f"- {option['airline']} "
                            f"{option['flight_number']} "
                            f"(${option['price']})"
                        )

                    else:

                        print(option)

            else:

                print(
                    "Agent: No alternative transportation was found."
                )

        elif route.category == "Escalation":

            result = escalate_to_human.invoke(
                {
                    "case_id": context.user_id
                }
            )

            print(
                f"Agent: {result['message']}"
            )


if __name__ == "__main__":
    run_agent()
