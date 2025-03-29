from agents_list import Agent
from system_prompts import brain_system_prompt
from agents_list.planner_agent import planner_agent
from agents_list.retriever_agent import retriever_agent


brain_agent = Agent(
    name="brain_agent",
    instructions=brain_system_prompt,
    tools=[planner_agent.as_tool, retriever_agent.as_tool],  # Assuming retriever_agent is defined elsewhere
    model="o3-mini",
    output_type=str,
    handoff_agent=[],  # Handoff to planner_agent after processing
)  # type: ignore
