from agents_list import Agent
from system_prompts import brain_system_prompt
from agents_list.planner_agent import planner_agent

brain_agent = Agent(
    name="brain_agent",
    instructions=brain_system_prompt,
    tools=[planner_agent.as_tool],
    model="gpt-4o",
    output_type=str,
)  # type: ignore
