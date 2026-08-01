# WanderPath Travel Agency – MCP Server Lab

## Team Members

- Menna Sobhe
- Moun Reda
- Abdelrahman Eslam

---

# Company

**WanderPath Travel Agency**

## Industry

Travel & Tourism

---

# Project Overview

This project implements a secure **Model Context Protocol (MCP) Server** for a travel agency. Instead of allowing an AI assistant to access the company database directly, the MCP Server exposes controlled tools, resources, and prompts while enforcing validation, authorization, and business rules.

The project demonstrates how an MCP-compliant server can safely connect Large Language Models (LLMs) with enterprise data.

---

# Problem Statement

WanderPath Travel Agency handles customer requests related to:

- Flight bookings
- Flight delays
- Cancellations
- Refund requests
- Rebooking
- Customer support escalations

Traditionally, employees search multiple systems manually to retrieve this information. Giving an AI assistant direct database access would introduce serious security and authorization risks.

The goal of this project is to build a secure MCP Server that allows an AI Agent to access company data safely through controlled interfaces instead of executing raw database queries.

---

# Why MCP?

Model Context Protocol provides a standardized and secure communication layer between AI models and enterprise systems.

Instead of exposing the database directly, the MCP Server:

- Controls tool access
- Validates every request
- Enforces authorization rules
- Exposes reusable resources
- Provides reusable prompts
- Supports runtime protocol features

This makes the system safer, more maintainable, and easier to extend.

---

# Project Structure

```text
.
├── README.md
├── main.py
├── requirements.txt
├── pyproject.toml
├── uv.lock
├── .gitignore
├── .python-version
├── __init__.py
│
├── agent/
│   ├── __init__.py
│   ├── README.md
│   ├── agent.py
│   ├── integration.py
│   ├── schema.py
│   ├── archive/
│   ├── routing/
│   └── unconstrained_react/
│
├── client/
│   └── client.py
│
├── db/
│   ├── schema.sql
│   ├── data.sql
│   └── erd.png
│
├── server/
│   ├── __init__.py
│   ├── README.md
│   └── server.py
│
├── shared/
│   ├── data/
│   ├── authorization.py
│   ├── database.py
│   ├── prompts.py
│   ├── resources.py
│   ├── validation.py
│   └── tricky_inputs.json
│
└── tools/
    ├── __init__.py
    ├── booking_tools.py
    ├── customer_tools.py
    ├── escalation_tools.py
    ├── finance_and_decision_tools.py
    ├── travel_status_tools.py
    └── utilties.py
```

---

# Database Design

The project uses a **MySQL relational database**.

Main tables include:

- Airports
- Flights
- Customers
- Bookings
- Employees
- Refunds
- Escalations

The ERD represents all entity relationships and foreign-key constraints used throughout the system.

---

# MCP Server Features

The MCP Server provides secure access to company data through:

- Tools
- Resources
- Prompts
- Validation
- Authorization

The AI Agent never communicates directly with the database.

---

# Protocol Concerns

## Capability Negotiation

The server declares its supported capabilities during the initialization phase.

The client checks these capabilities before attempting to use optional features.

---

## Notifications

The available tool set changes dynamically according to the authenticated user's role.

Whenever permissions change, the server sends **tools/list_changed** notifications.

---

## Elicitation

Sensitive write operations require explicit human confirmation before completion.

The server pauses execution until approval is received.

---

## Resources

Static company information is exposed as read-only resources instead of executable tools.

Examples include:

- Refund Policy
- Travel Policies
- Airport Information

---

## Prompts

Reusable prompt templates are provided for common business tasks such as:

- Draft Refund Explanation
- Customer Response
- Escalation Summary

---

## Transport

The transport actually implemented in this project is **STDIO**.

That choice matches the problem well because the AI agent and MCP server are meant to run locally during the lab, allowing direct process-to-process communication with no network exposure for sensitive travel data.

**Streamable HTTP** is still a valid future deployment path for remote access or multiple clients, but it is not the transport built in this version.

---

## Progress Tracking

Long-running operations report execution progress to the client instead of blocking until completion.

---

## Defensive Tool Design

Every write tool includes:

- JSON Schema validation
- Server-side validation
- Authorization checks
- Business rule enforcement

No tool executes raw SQL received from the model.

---

# Agent Integration

The AI Agent communicates exclusively with the MCP Server.

Workflow:

```text
User
 ↓
AI Agent
 ↓
MCP Server
 ↓
MySQL Database
 ↓
MCP Server
 ↓
AI Agent
 ↓
User
```

---

# Resources

The server exposes read-only resources including:

- Refund Policy
- Travel Policies
- Airport Status

---

# Prompts

Reusable prompts include:

- Draft Refund Explanation
- Generate Escalation Report
- Customer Support Response

---

# Running the Project

## 1. Configure Environment

Create a `.env` file:

```env
DB_HOST=localhost
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=travel_agency
GOOGLE_API_KEY=your_api_key
```

---

## 2. Initialize Database

```bash
mysql < db/schema.sql
mysql < db/data.sql
```

---

## 3. Run the MCP Server

```bash
python server/server.py
```

---

## 4. Run the AI Agent

```bash
python agent/client.py
```

---

# Technologies

- Python
- MySQL
- Model Context Protocol (MCP)
- LangChain
- Google Gemini 2.5 Flash
- JSON Schema
- python-dotenv

---

# Security Features

- No direct database access
- Server-side validation
- Authorization checks
- JSON Schema validation
- Role-based permissions
- Secure tool execution

---

# Future Improvements

- Streamable HTTP deployment
- Live airline APIs
- Real-time flight tracking
- Multi-user authentication
- Audit logging
- Dashboard for monitoring MCP requests

---

# test project

```bash
python main.py
```
