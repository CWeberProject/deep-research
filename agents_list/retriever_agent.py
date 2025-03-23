from agents_list import Agent
from tools import fetch_tool, google_tool
from system_prompts import retriever_system_prompt

retriever_agent = Agent(
    name="retriever_agent",
    instructions=retriever_system_prompt,
    tools=[fetch_tool, google_tool],
    description="""Web Search Agent. Receives a Google Search query (string) as input from
    the brain agent, and uses tools to do the google search, fetch the top 10 URLs for it, 
    and retrieves and parses their content. Finally, it summarizes all of the extracted 
    content to pass it to the writer agent.""",
    model="gpt-4o",
    model_settings={"tool_choice": "required"},
    output_type=str,
)  # type: ignore