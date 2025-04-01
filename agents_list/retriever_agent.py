from agents import Agent
from tools.fetch_tool import fetch_tool
from tools.web_research import web_research
from system_prompts import retriever_system_prompt

retriever_agent = Agent(
    name="Retriever Agent",
    instructions=retriever_system_prompt,
    tools=[fetch_tool, web_research],
    model="gpt-4o-mini",
)  # type: ignore