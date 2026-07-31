from typing import Literal, get_args

from pydantic import BaseModel, ConfigDict, Field


MAX_STEPS = 6
VALIDATION_RETRIES = 2


ActionName = Literal[
    "get_booking_history",
    "get_flight_status",
    "get_delay_duration",
    "check_alternative_transport",
    "check_refund_eligibility",
    "calculate_refund_amount",
    "refund_with_confirmation",
    "issue_travel_voucher",
    "escalate",
    "end_conversation",
    "evaluate_cancellation_reason",
    "final_answer",
    "escalate",
    "end_conversation"
]

ALLOWED_ACTIONS = set(get_args(ActionName))
TERMINAL_ACTIONS = {"escalate", "end_conversation", "final_answer"}


class AgentStep(BaseModel):
    thought: str
    action: ActionName
    action_input: dict = Field(default_factory=dict)
    is_final: bool


class StrictInput(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EmptyInput(StrictInput):
    pass


class FlightInput(StrictInput):
    flight_id: str


class DestinationInput(StrictInput):
    destination: str


class BookingInput(StrictInput):
    booking_id: str


class EscalationInput(StrictInput):
    case_id: str


class AnswerInput(StrictInput):
    answer: str


ACTION_INPUT_SCHEMAS = {
    "get_booking_history": EmptyInput,
    "get_flight_status": FlightInput,
    "get_delay_duration": FlightInput,
    "check_alternative_transport": DestinationInput,
    "check_refund_eligibility": BookingInput,
    "calculate_refund_amount": BookingInput,
    "refund_with_confirmation": BookingInput,
    "issue_travel_voucher": BookingInput,
    "escalate": EscalationInput,
    "end_conversation": AnswerInput,
    "final_answer": AnswerInput,
}
