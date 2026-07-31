import asyncio
from pydantic import ValidationError
from dataclasses import dataclass
from langchain.messages import AIMessage, HumanMessage, SystemMessage
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from .schema import (
    ACTION_INPUT_SCHEMAS,
    AgentStep,
    MAX_STEPS,
)


load_dotenv()


@dataclass
class AgentContext:
    user_id: str


@dataclass
class ToolRuntimeShim:
    context: AgentContext


def build_system_prompt(tool_names):

    tool_list = "\n".join(tool_names)

    return f"""
You are a constrained travel support agent.

Use ONLY these tools:
{tool_list}
Additional Instructions:
1. Do NOT retry calling a tool if you already received an Observation from it.
2. Once you have gathered enough information to answer the user's question, set your action to 'final_answer' and provide the final response in 'action_input.answer'.
3. Do NOT invent or call tools that are not listed above.

Think step by step and return only the structured response.
"""

def build_structured_model():
    return init_chat_model(
        model="google_genai:gemini-3.5-flash-lite",
        max_tokens=1024,
        max_retries=3,
    ).with_structured_output(AgentStep)

#groq
# def build_structured_model():
#     return init_chat_model(
#         model="llama-3.3-70b-versatile",
#         model_provider="groq",
#         max_tokens=1024,
#         max_retries=3,
#     ).with_structured_output(AgentStep)

#  # Issue 6
async def discover_tools(client):
    """Dynamically fetches and registers available tools from the MCP Client."""
    tools_list = await client.get_tools()
    # turns from list to dict
    tools_dict = {tool.name: tool for tool in tools_list}

    return tools_dict  # Dict: {tool_name: tool_instance}

#   # Issue  10    
def validate_step(step, tools) -> bool:
    valid_actions = {"final_answer", "end_conversation", "escalate"}
    return step.action in valid_actions or step.action in tools

#  # Issue 7 
#  Issue #7: Tool Execution Engine
async def tool_call(step: AgentStep, tools: dict, context: AgentContext = None):
    """Validates payload schema, injects runtime context, and executes tool."""
    tool = tools[step.action]

    payload = step.action_input

    # 1. Pydantic validation if schema exists
    schema_cls = ACTION_INPUT_SCHEMAS.get(step.action)
    if schema_cls:
        validated_input = schema_cls(**step.action_input)
        payload = validated_input.model_dump()

    # 2. Inject context (user_id) if missing
    if context and isinstance(payload, dict):
        if step.action in {
            "get_booking_history",
            "get_customer_profile",
        }:
            payload.setdefault("user_id", context.user_id)
    # 3. Asynchronous execution
    result = await tool.ainvoke(payload)
    return result

def handle_final_action(step):

    if step.action == "final_answer":
        print(step.action_input["answer"])
        return True

    if step.action == "end_conversation":
        if step.action_input:
            print(step.action_input.get("answer", "Goodbye!"))
        else:
            print("Goodbye!")
        return True

    if step.action == "escalate":
        print("Escalating to human support...")
        return True

    return False

#observation
def handle_tool_result(messages, step, result):
    print(f"Observation from {step.action}: {result}")
    messages.append(
        HumanMessage(
            content=f"Observation from {step.action}: {result}"
        )
    )

async def run_agent(client, user_input: str, user_id: str = "C001"):
    tools = await discover_tools(client)
    context = AgentContext(user_id=user_id)
    system_prompt = build_system_prompt(list(tools.keys()))
    model = build_structured_model()
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_input),
    ]

    # (Agent Loop)
    for step_num in range(MAX_STEPS):
        print(f"\n--- Step {step_num + 1} ---")
        
        step: AgentStep = await model.ainvoke(messages)
        print(f"Thought: {step.thought}")
        print(f"Action: {step.action}")
        messages.append(
            AIMessage(content=f"Thought: {step.thought}\nAction: {step.action}\nInput: {step.action_input}")
        )
        #(Final Action)
        if handle_final_action(step):
            return step
        
        #  Step Validation check
        if not validate_step(step, tools):
            messages.append(
                HumanMessage(
                    content=f"Error: '{step.action}' is not a valid tool. Choose from: {list(tools.keys())}"
                )
            )
            continue


        # (MCP Tool Execution)
        try:
            result = await tool_call(step, tools, context=context) 
            handle_tool_result(messages, step, result)

            messages.append(
                HumanMessage(content=f"Observation from tool '{step.action}': {result}")
            )  
            
        except ValidationError as e:
            messages.append(
                HumanMessage(content=f"Invalid arguments for {step.action}: {e.errors()}")
            )
        except Exception as e:
            messages.append(
                HumanMessage(content=f"Error executing tool {step.action}: {str(e)}")
            )
    print("Reached maximum execution steps without final answer.")
    return None


async def main():
    print("Agent module ready. Use run_agent(client, user_input) inside an active client session.")


if __name__ == "__main__":
    asyncio.run(main())