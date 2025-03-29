from agents import Agent
from tools.q_and_a_tool import q_and_a_tool
from system_prompts import planner_system_prompt

planner_agent = Agent(
    name="enhancer_agent",
    instructions=planner_system_prompt,
    tools=[q_and_a_tool],
    model="o3-mini",
)