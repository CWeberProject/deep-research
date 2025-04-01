from agents import Agent
from system_prompts import writer_system_prompt

writer_agent = Agent(
    name="Writer Agent",
    instructions=writer_system_prompt,
    model="gpt-4o",
)