# Agent Design Lab – Four Agent Architectures

## Team Members

- Menna Sobhe
- Abdelrahman Eslam
- Youssef Abdelrahman

---

# Company

**Wander path travel A**

## Industry

Travel Agency

---

# Problem Statement

Wander Path Travel receives thousands of customer support requests every day related to flight bookings, delays, cancellations, and travel itinerary changes.

The system must decide the next action depending on several factors such as:

- Delay duration
- Flight status
- Customer VIP status
- Connection risk
- Weather conditions
- Available alternative flights
- Refund eligibility

A simple script is not enough because many decisions depend on information retrieved during execution (checking flights, customer profile, company policy, etc.).

This makes it an ideal problem for comparing different agent architectures.

---

# Why an Agent Instead of a Script?

A traditional script works well only for fixed rules.

However, real customer requests require:

- Looking up customer information
- Checking flight status
- Searching for available alternatives
- Applying airline policies
- Deciding whether to escalate the case

Some of these decisions depend on previous tool outputs, making agent-based reasoning more appropriate.

---

# Project Structure

```
.
├── README.md
├── reactive/
│   ├── README.md
│   └── main.py
├── unconstrained_react/
│   ├── README.md
│   └── main.py
├── routing/
│   ├── README.md
│   └── main.py
└── constrained_react/
    ├── README.md
    ├── main.py
    ├── schema.py
    └── tools.py
```

Each folder contains an independent implementation of the same travel support problem using a different agent architecture.

---

# Agent Architectures

## 1. Reactive Agent (Rule-Based)

A pure rule-based system with no LLM.

It relies entirely on hard-coded conditions.

Example:

- Delay < 30 minutes → Inform customer
- Delay > 180 minutes → Offer refund
- Flight canceled → Create support ticket

### Characteristics

- No model calls
- Fast
- Cheap
- Predictable

### Limitations

Cannot combine multiple conditions or reason about previous tool outputs.

---

## 2. Unconstrained ReAct Agent

This version gives the LLM complete freedom.

The model decides:

- which tools to call
- in what order
- when to stop reasoning

No schema validation.

No maximum reasoning steps.

### Characteristics

- Flexible
- Handles complex scenarios
- Better reasoning

### Limitations

- Higher token usage
- Less predictable
- May call unnecessary tools

---

## 3. Deterministic Routing Agent

Only one constrained LLM call is used.

The model classifies the request into predefined categories such as:

- Refund
- Rebooking
- Flight Information
- Escalation

After classification, deterministic Python code performs the remaining work.

### Characteristics

- Low cost
- Fast
- Easy to test
- Predictable behavior

### Limitations

Cannot perform multi-step reasoning.

---

## 4. Constrained ReAct Agent

This version combines reasoning with strict safety constraints.

It includes:

- JSON schema validation
- Tool allow-list
- Maximum reasoning steps
- Explicit final answer or escalation

### Constraints

- Schema validation using Pydantic
- Tool allow-list
- MAX_STEPS = 6

### Characteristics

- Safe
- Flexible
- Reliable
- Production-friendly

---

# Running the Project

Each implementation can be run independently.

## Reactive

```

cd reactive
python main.py

```

## Unconstrained ReAct

```

cd unconstrained_react
python main.py

```

Requires:

- API key
- `.env`

Example:

```

GOOGLE\_API\_KEY=YOUR\_KEY

```

---

## Routing

```

cd routing
python main.py

```

Requires the same API configuration.

---

## Constrained ReAct

```

cd constrained_react
python main.py

```

Requires:

- API key
- `.env`

Important files:

- `schema.py`
- `tools.py`
- `main.py`

---

# Comparison

| Architecture          |          LLM Calls | Cost     | Latency   | Strengths                   | Tricky Input Result                                  |
| --------------------- | -----------------: | -------- | --------- | --------------------------- | ---------------------------------------------------- |
| Reactive              |                  0 | Very Low | Very Fast | Simple, predictable         | Failed to combine multiple conditions                |
| Unconstrained ReAct   |           Multiple | High     | High      | Flexible reasoning          | Solved the case but sometimes used unnecessary tools |
| Deterministic Routing |                  1 | Low      | Fast      | Easy to test                | Misclassified some complex requests                  |
| Constrained ReAct     | Multiple (bounded) | Medium   | Medium    | Safe and reliable reasoning | Correctly handled the case within `MAX_STEPS`        |

---

# Example Test Case

**Scenario**

Customer:

- Flight delayed by 4 hours
- VIP passenger
- High connection risk
- Alternative flight available

Expected behavior:

| Agent               | Result                                                                                 |
| ------------------- | -------------------------------------------------------------------------------------- |
| Reactive            | Refund only                                                                            |
| Unconstrained ReAct | May check alternatives and offer rebooking                                             |
| Routing             | Routes to Rebooking                                                                    |
| Constrained ReAct   | Checks tools, validates reasoning, then recommends rebooking with escalation if needed |

---

# Technologies

- Python
- LangChain
- Google Gemini API
- Pydantic
- dotenv

---

## Model

The **Unconstrained ReAct**, **Deterministic Routing**, and **Constrained ReAct** agents use **Google Gemini 2.5 Flash** through the Google AI Studio API.

The **Reactive Agent** does not require an LLM.


## Allowed Tools

The LLM-powered agents use a restricted set of tools to interact with the travel system.

```
tools/
├── __init__.py
├── booking_tools.py
├── customer_tools.py
├── escalation_tools.py
├── finance_and_decision_tools.py
├── travel_status_tools.py
└── utilities.py
```

These tools provide functionality for:

- Booking management
- Customer information lookup
- Travel and flight status checking
- Refund and financial decisions
- Human escalation
- Utility functions

---

# Future Improvements

- Add memory for returning customers
- Connect to a real airline database
- Integrate with live flight APIs
- Add human-in-the-loop approval for sensitive decisions
