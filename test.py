import sys
import asyncio
from agents_list.enhancer_agent import enhancer_agent
from agents_list.brain_agent import brain_agent
from agents_list.retriever_agent import retriever_agent
from openai.types.responses import ResponseTextDeltaEvent


from agents import Runner, RunHooks, RunContextWrapper, Agent, Tool


class ContentRunHooks(RunHooks):
    def __init__(self):
        super().__init__()
        self.content_list = []
    async def on_tool_start(self, context: RunContextWrapper, agent: Agent, tool: Tool) -> None:
        print(f"Outil {tool.name} est sur le point d'être appelé")
    
    async def on_tool_end(self, context: RunContextWrapper, agent: Agent, tool: Tool, result: str) -> None:
        if tool.name == "web_research":
            print(f"Résultat de l'outil {tool.name} : {result}")
        if tool.name == "fetch_tool":
            self.content_list.append(result)

content_retrieval_hook = ContentRunHooks()

async def run_research():
    """
    Runs the brain agent interactively in the terminal.
    Takes a research query from the user and processes it directly through the brain agent.
    """
    print("\n=== Research Query Processor ===")
    print("Enter your research query below. The brain agent will process it directly.")
    print("(Type 'exit' to quit)")
    print("\n--- Your Research Query ---")
    
    # Collect multi-line input for the research query
    lines = []
    while True:
        line = input()
        if line.lower() == 'exit':
            print("Exiting the program.")
            return
        if not line and lines:  # Empty line ends input, but only if we have some content
            break
        lines.append(line)
    
    if not lines:
        print("No query provided. Exiting.")
        return
    
    # Combine the lines into the research query
    user_query = '\n'.join(lines)
    
    print("\nProcessing your query...\n")
    
    try:
        # Run the brain agent directly with the user's query
        print("\n=== Final Report ===\n")
        final_report = await Runner.run(retriever_agent, user_query, hooks=content_retrieval_hook)
        print(final_report.final_output)
        print("\n====================\n")
        print("\n===Content List===\n")
        print(content_retrieval_hook.content_list)
        
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please try again or check your configuration.")

if __name__ == "__main__":
    try:
        asyncio.run(run_research())
    except KeyboardInterrupt:
        print("\nProcess interrupted. Exiting.")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1)
