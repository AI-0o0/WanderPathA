from pydantic import ValidationError
from dataclasses import dataclass
from langchain.messages import AIMessage, HumanMessage, SystemMessage
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from schema import (
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

Think step by step.

Return only the structured response.
"""

def build_structured_model():
    return init_chat_model(
        model="google_genai:gemini-3.5-flash-lite",
        max_tokens=1024,
        max_retries=3,
    ).with_structured_output(AgentStep)

#  # Issue 6
# async def discover_tools(client):


#   # Issue  10    
# def validate_step(step, tools) -> bool:

#  # Issue 7 
# async def tool_call(step: AgentStep, tools: dict, context: AgentContext = None):


def handle_final_action(step):

    if step.action == "final_answer":
        print(step.action_input["answer"])
        return True

    if step.action == "end_conversation":
        print(step.action_input["answer"])
        return True

    if step.action == "escalate":
        print("Escalating to human support...")
        return True

    return False

#observation
def handle_tool_result(messages, step, result):

    messages.append(
        HumanMessage(
            content=f"Observation from {step.action}: {result}"
        )
    )

async def run_agent(client, user_input: str, user_id: str = "C001"):
    tools = await discover_tools(client)
    
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
        #(Final Action)
        if handle_final_action(step):
            return step

        if step.action not in tools:
            messages.append(
                HumanMessage(content=f"Error: '{step.action}' is not a valid tool. Choose from: {list(tools.keys())}")
            )
            continue

        # (MCP Tool Execution)
        try:
            result = await tool_call(step, tools)
            handle_tool_result(messages, step, result)
        except ValidationError as e:
            # إرجاع خطأ الـ Schema للـ LLM علشان يعمل Self-Correction
            messages.append(
                HumanMessage(content=f"Invalid arguments for {step.action}: {e.errors()}")
            )
        except Exception as e:
            messages.append(
                HumanMessage(content=f"Error executing tool {step.action}: {str(e)}")
            )
    print("Reached maximum execution steps without final answer.")
    return None


if __name__ == "__main__":
    run_agent()
