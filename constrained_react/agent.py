from dataclasses import dataclass

from langchain.messages import AIMessage, HumanMessage, SystemMessage
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from constrained_react.schema import (
    AgentStep,
    MAX_STEPS,
)
from tools.customer_tools import GetBookingHistory
from tools.travel_status_tools import (
    get_flight_status,
    get_delay_duration,
    check_alternative_transport,
)
from tools.finance_and_decision_tools import (
    CheckRefundEligibility,
    CalculateRefundAmount,
    ProcessRefund,
    IssueTravelVoucher,
)
from tools.escalation_tools import escalate_to_human


load_dotenv()


@dataclass
class AgentContext:
    user_id: str


@dataclass
class ToolRuntimeShim:
    context: AgentContext


SYSTEM_PROMPT = ("""
You are a constrained travel support agent.
The customer is already authenticated.
Think step by step.
You may only choose one action at a time.
Use tool observations instead of guessing booking, flight, refund, or transport details.
If alternative transportation is available, suggest it before offering a refund.
Allowed actions are:

get_booking_history
get_flight_status
get_delay_duration
check_alternative_transport
check_refund_eligibility
calculate_refund_amount
process_refund
issue_travel_voucher
escalate
end_conversation
final_answer

Action input formats:
get_booking_history: {}
get_flight_status: {"flight_id": "<flight id>"}
get_delay_duration: {"flight_id": "<flight id>"}
check_alternative_transport: {"destination": "<airport code>"}
check_refund_eligibility: {"booking_id": "<booking id>"}
calculate_refund_amount: {"booking_id": "<booking id>"}
process_refund: {"booking_id": "<booking id>"}
issue_travel_voucher: {"booking_id": "<booking id>"}
escalate: {"case_id": "<booking id or case id>"}
end_conversation: {"answer": "<brief goodbye message>"}
final_answer: {"answer": "<plain text response to the customer>"}

Use final_answer when the customer's current request is answered and the conversation should stay open.
Use end_conversation only when the customer says goodbye, asks to exit, or clearly wants to stop chatting.
Set is_final to true only when action is final_answer, end_conversation, or escalate.
Set is_final to false for every tool action.
Return only the structured response.
Never explain outside the schema.
""")


TOOLS = {
    "get_booking_history": GetBookingHistory,
    "get_flight_status": get_flight_status,
    "get_delay_duration": get_delay_duration,
    "check_alternative_transport": check_alternative_transport,
    "check_refund_eligibility": CheckRefundEligibility,
    "calculate_refund_amount": CalculateRefundAmount,
    "process_refund": ProcessRefund,
    "issue_travel_voucher": IssueTravelVoucher,
}


def build_structured_model():
    return init_chat_model(
        model="google_genai:gemini-3.5-flash-lite",
        max_tokens=1024,
        max_retries=3,
    ).with_structured_output(AgentStep)


def run_agent(user_id: str = "C001"):
    print("Welcome to the Constrained Travel Support Agent!")

    context = AgentContext(user_id=user_id)
    structured_model = build_structured_model()
    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    while True:
        user_input = input("User: ").strip()
        if not user_input:
            continue

        messages.append(HumanMessage(content=user_input))

        for _ in range(MAX_STEPS):
            step = structured_model.invoke(messages)
            messages.append(AIMessage(content=step.model_dump_json()))

            if step.action == "escalate":
                result = escalate_to_human.invoke(step.action_input)
                print(f"Agent: {result.get('message', 'Cant help you with that, escalating to human support.')}")
                break

            if step.action == "final_answer":
                print(f"Agent: {step.action_input['answer']}")
                break

            if step.action == "end_conversation":
                print(f"Agent: {step.action_input['answer']}")
                return

            if step.action == "get_booking_history":
                result = GetBookingHistory.func(ToolRuntimeShim(context=context))
            else:
                result = TOOLS[step.action].invoke(step.action_input)

            messages.append(HumanMessage(content=f"Observation from {step.action}: {result}"))
        else:
            result = escalate_to_human.invoke({"case_id": user_id})
            print(
                "Agent: I reached my step limit before resolving this. "
                f"{result['message']}"
            )


if __name__ == "__main__":
    run_agent()
