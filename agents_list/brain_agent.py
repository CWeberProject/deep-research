from agents import Agent
from system_prompts import brain_system_prompt
from agents_list.planner_agent import planner_agent
from agents_list.retriever_agent import retriever_agent
from agents_list.writer_agent import writer_agent


brain_agent = Agent(
    name="Brain Agent",
    instructions=brain_system_prompt,
    tools=[planner_agent.as_tool(
        tool_name="planner_agent",
        tool_description="This agent plans the content structure and google queries.",
    ), retriever_agent.as_tool(
        tool_name="retriever_agent",
        tool_description="This agent retrieves content from various web sources based on a google query.",
    )],  # Assuming retriever_agent is defined elsewhere
    model="o3-mini",
    handoffs=[writer_agent],  # Handoff to planner_agent after processing
)  # type: ignore
