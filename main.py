import sys
import asyncio
from agents_list.enhancer_agent import enhancer_agent
from agents_list.brain_agent import brain_agent

from agents import Runner

content_list = []


async def run_enhancer():
    """
    Runs the enhancer agent interactively in the terminal.
    Takes a research query from the user and processes it through the enhancer agent.
    """
    print("\n=== Research Query Enhancer ===")
    print("Enter your research query below. The enhancer will analyze it and may ask clarifying questions.")
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
        # Run the enhancer agent with the user's query
        enhanced_query = await Runner.run(enhancer_agent, user_query)
        
        # Display the final enhanced research directive
        print("\n=== Enhanced Research Directive ===\n")
        print(enhanced_query.final_output)
        print("\n===================================\n")

        # Run the brain agent with the enhanced query
        final_report = await Runner.run(brain_agent, enhanced_query.final_output)
        print("\n=== Final Report ===\n")
        print(final_report.final_output)
        print("\n====================\n")
        
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please try again or check your configuration.")

if __name__ == "__main__":
    try:
        asyncio.run(run_enhancer())
    except KeyboardInterrupt:
        print("\nProcess interrupted. Exiting.")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1)
