# Reactive Agent

## Description

This implementation uses a **rule-based (Reactive) agent** with no Large Language Model (LLM).

The agent follows predefined `if/else` rules to determine the next action based on the customer's travel situation. Every decision is deterministic and does not involve reasoning or planning.

## Decision Rules

The agent follows these rules:

1. **Flight Cancelled**
   - Check for alternative transportation.
   - If available, recommend the alternative.
   - Otherwise:
     - If the booking is eligible for a refund, process the refund.
     - If not eligible, escalate the case to a human agent.

2. **Delay Greater Than 6 Hours**
   - Issue a hotel/travel voucher.

3. **Delay Less Than or Equal to 2 Hours**
   - Notify the customer to wait for the flight.

4. **All Other Cases**
   - Escalate the request to a human support agent.

## Characteristics

- No LLM calls
- Fast execution
- Low cost
- Fully deterministic
- Easy to test

## Limitations

This agent cannot:

- Combine multiple conditions effectively.
- Adapt to new or unseen situations.
- Perform multi-step reasoning.
- Make decisions based on previous tool outputs beyond the predefined rules.

## Required Tools

The agent uses the following tool modules:

- `travel_status_tools.py`
- `finance_and_decision_tools.py`
- `escalation_tools.py`

## Run

```bash
python main.py
```

No API key or language model is required.
