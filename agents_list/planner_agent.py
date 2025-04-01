from agents import Agent
from system_prompts import planner_system_prompt

planner_agent = Agent(
    name="Planner Agent",
    instructions=planner_system_prompt,
    model="gpt-4o-mini",
)