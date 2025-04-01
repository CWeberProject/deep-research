from agents import Agent
from tools.q_and_a_tool import q_and_a_tool
from system_prompts import enhancer_system_prompt

enhancer_agent = Agent(
    name="Enhancer Agent",
    instructions=enhancer_system_prompt,
    tools=[q_and_a_tool],
    model="o3-mini",
)