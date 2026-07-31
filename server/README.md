# Transport Configuration

## STDIO (Default)

- Used for direct process-to-process communication
- Suitable for: Testing, local development, single machine
- Justification: Simpler to test, no network overhead

## HTTP (Alternative)

- Streamable HTTP at localhost:8000/mcp
- Suitable for: Remote access, multiple clients