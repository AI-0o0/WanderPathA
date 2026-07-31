import sys
import os
from fastmcp import FastMCP , Context
from mcp.types import ElicitRequestedSchema
from typing import Literal

import asyncio

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)

import mcp.types as types 
from shared.database import get_connection



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
    get_nearby_airports,
    get_flight_options
)
from tools.customer_tools import (
    get_customer_profile,
    get_booking_history
)
from tools.finance_and_decision_tools import ProcessRefund, CalculateRefundAmount

# Initialize FastMCP server for WanderPathA
mcp = FastMCP("WanderPathA Travel Agent Server")

# Register Existing Tools
mcp.tool()(get_flight_status.func)
mcp.tool()(get_weather.func)
mcp.tool()(get_delay_duration.func)
mcp.tool()(check_disruption_reason.func)
mcp.tool()(get_nearby_airports.func)
mcp.tool()(get_flight_options.func)
mcp.tool()(get_customer_profile.func)
mcp.tool()(get_booking_history.func)

# Elication
@mcp.tool()
async def refund_with_confirmation(
    ctx: Context,
    booking_id: int,
):
    """Process a refund after explicit user confirmation."""

    print("=== refund_with_confirmation started ===")

    employee_id = 3

    print("1. Reporting progress...")
    await ctx.report_progress(
        progress=10,
        total=100,
        message="Calculating refund amount..."
    )

    print("2. Calculating refund amount...")
    refund_amount = CalculateRefundAmount.func(
        booking_id=booking_id
    )
    print(f"Refund amount = {refund_amount}")

    await asyncio.sleep(1)

    print("3. Reporting progress...")
    await ctx.report_progress(
        progress=40,
        total=100,
        message="Waiting for customer confirmation..."
    )

    print("4. Waiting for elicitation...")
    result = await ctx.elicit(
        message=(
            f"You are about to refund ${refund_amount:.2f} "
            f"for booking {booking_id}.\n\n"
        ),
        response_type=Literal["confirm", "cancel"],
    )

    print("Elicitation result:", result)

    if result.action != "accept":
        print("User declined.")
        return {
            "status": "Cancelled",
            "message": "Refund cancelled by user."
        }

    if result.data != "confirm":
        print("User did not type confirm.")
        return {
            "status": "Cancelled",
            "message": "Refund cancelled by user."
        }

    print("5. Reporting progress...")
    await ctx.report_progress(
        progress=70,
        total=100,
        message="Processing refund..."
    )

    await asyncio.sleep(1)

    print("6. Calling ProcessRefund...")
    refund_result = ProcessRefund.func(
        booking_id=booking_id,
        employee_id=employee_id,
        refund_amount=refund_amount,
    )

    print("ProcessRefund returned:", refund_result)

    print("7. Reporting completion...")
    await ctx.report_progress(
        progress=100,
        total=100,
        message="Refund completed."
    )

    print("=== refund_with_confirmation finished ===")

    return refund_result

# Sampling 
@mcp.tool()
async def evaluate_cancellation_reason(
    ctx: Context,
    booking_id: int,
    user_reason: str = "",
    cancellation_reason: str = "",
    reason: str = "",
    user_id: str = "",
) -> str:
  """Evaluates refund eligibility using LLM sampling with automated fallback."""
  eval_reason = reason or user_reason or cancellation_reason or "Emergency"
  b_id = booking_id or "BK-9921"

  prompt = (
      f"Evaluate the travel cancellation reason: '{eval_reason}'. Does it"
      " qualify for a 100% full refund according to emergency travel policy?"
      " Respond ONLY with 'APPROVED' or 'DENIED' followed by a brief"
      " explanation."
  )

  try:
    sampling_response = await ctx.session.create_message(
        messages=[{"role": "user", "content": prompt}], max_tokens=100
    )

    llm_output = ""
    if hasattr(sampling_response, "content") and sampling_response.content:
      if isinstance(sampling_response.content, list):
        llm_output = "\n".join(
            [getattr(c, "text", str(c)) for c in sampling_response.content]
        )
      else:
        llm_output = getattr(
            sampling_response.content, "text", str(sampling_response.content)
        )

    return (
        f"Policy Evaluation Result for Booking {b_id} (via LLM"
        f" Sampling):\n{llm_output.strip()}"
    )

  except Exception as e:
    # Fallback 
    print(f"[Sampling Attempt Logged]: {e}")

    reason_lower = eval_reason.lower()
    if any(
        kw in reason_lower
        for kw in [
            "flood",
            "weather",
            "medical",
            "emergency",
            "hospital",
            "submerged",
        ]
    ):
      return (
          f"Policy Evaluation Result for Booking {b_id}: APPROVED\nAnalysis:"
          " Severe emergency condition qualifies for 100% full refund under"
          " policy."
      )

    return (
        f"Policy Evaluation Result for Booking {b_id}: DENIED\nAnalysis:"
        " Reason does not qualify for full refund. Standard 20% cancellation"
        " fee applies."
    )
  
if __name__ == "__main__":
    transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"
    if transport == "stdio":
        sys.stderr.write("Starting WanderPathA Server [stdio]...")
        mcp.run(transport="stdio")
    elif transport == "http":
        sys.stderr.write("Starting WanderPathA Server [http:8000]...")
        mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)