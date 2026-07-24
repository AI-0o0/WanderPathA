import sys
from dotenv import load_dotenv
from dataclasses import dataclass

from langchain.agents import create_agent
from langchain.messages import AIMessage, HumanMessage, ToolMessage
from tools.booking_tools import GetFlightOptions, GetNearbyAirports
from tools.customer_tools import (GetBookingHistory,
                                  GetCustomerProfile,
                                  UpdateCustomerProfile)
from tools.utilties import SearchWeb, GetCurrentDate, EndConversation
from tools.travel_status_tools import (
    get_flight_status,
    get_delay_duration,
    check_alternative_transport,
    check_connection_risk,
    check_disruption_reason,
    get_estimated_departure,
    get_estimated_arrival
)
from tools.finance_and_decision_tools import (
    CheckRefundEligibility,
    CalculateCompensation,
    CalculateRefundAmount,
    ProcessRefund,
    IssueTravelVoucher,
)
from tools.escalation_tools import escalate_to_human

from pydantic import BaseModel
load_dotenv()

@dataclass
class AgentContext:
    user_id: str


SYSTEM_PROMPT = ("""
You are a Travel Support Agent.
Help customers resolve issues that occur after they have booked their trip, such as flight delays, cancellations, rebooking, refunds, compensation, travel vouchers, and customer booking inquiries.
Always use the available tools to retrieve customer, booking, and flight information instead of making assumptions.
If alternative transportation or rebooking is available, suggest it before offering a refund.
Use the web search tool only when the required information is unavailable through the provided tools.
If a tool returns no data, tell the user honestly instead of guessing.
If the user wants to end the conversation, call the end_conversation tool.
Respond in concise plain text without markdown.
""")

TOOLS = [
    GetCurrentDate,
    SearchWeb,
    GetCustomerProfile,
    GetBookingHistory,
    UpdateCustomerProfile,
    GetNearbyAirports,
    GetFlightOptions,
    get_flight_status,
    get_delay_duration,
    check_disruption_reason,
    get_estimated_departure,
    get_estimated_arrival,
    check_connection_risk,
    check_alternative_transport,

    CheckRefundEligibility,
    CalculateRefundAmount,
    CalculateCompensation,
    ProcessRefund,
    IssueTravelVoucher,

    escalate_to_human,

    EndConversation,
]

agent = create_agent(
    model="google_genai:gemini-3.5-flash-lite",
    tools=TOOLS,
    system_prompt=SYSTEM_PROMPT,
)

def run_agent():

    print("Welcome to the Travel Support Agent!")

    user_id = "C001" 
    context = AgentContext(user_id=user_id)

    messages = []
    ended = False
    while True:

        user_input = input("User: ")
        # Add the new user message to the conversation history
        messages.append(HumanMessage(content=user_input))

        stream = agent.stream(
            {"messages": messages},
            context=context,
            stream_mode="values",
        )


        for snapshot in stream:
            latest_message = snapshot["messages"][-1]
            if isinstance(latest_message, AIMessage):
                if latest_message.tool_calls:
                    print(f"Calling tools: {[tc['name'] for tc in latest_message.tool_calls]}")
                    if any(tc["name"] == "end_conversation" for tc in latest_message.tool_calls):
                        ended = True
                if latest_message.content:
                    print(f"Agent: {latest_message.content}")
            if isinstance(latest_message, ToolMessage):
                print(f"Tool Result: {latest_message.content}")
            messages = snapshot["messages"] 
        if ended:
            print("thank you for using the Travel Support Agent. Goodbye!")
            sys.exit(0)
        

if __name__ == "__main__":
    run_agent()

