from agents_list import Agent
from tools import q_and_a_tool
from system_prompts import enhancer_system_prompt

enhancer_agent = Agent(
    name="enhancer_agent",
    instructions=enhancer_system_prompt,
    tools=[q_and_a_tool],
    description="""Enhancer Agent. Receives the initial user query (string) as input directly from the user,
    analyzes it, and after having understood the user's intent, decides whether to ask clarifying questions
    or to create a research directive. If clarifying questions are needed, it uses the q_and_a tool to ask them
    and waits for the user's response. Once the user has answered all questions, it creates the research
    directive and passes it to the brain agent.""",
    model="o3-mini-2025-01-31",
    model_settings={"tool_choice": "required"},
    output_type=str,
)