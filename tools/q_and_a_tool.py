from agents import function_tool

@function_tool(name_override="qa")
def q_and_a_tool(input_text: str) -> str:
    """
    A tool that displays text with a list of questions to the user, waits for their reply, and returns their response.
    
    Args:
        input_text (str): The text with questions to display to the user (list of questions the enhancer agent needs to fully understand the user's intent).
    
    Returns:
        str: The user's response.
    """
    # Display the agent's text to the user
    print("\n--- Agent's Message ---")
    print(input_text)
    print("\n--- Your Response ---")
    
    # Collect user input (handles multi-line input until user enters an empty line)
    lines = []
    while True:
        line = input()
        if not line:
            break
        lines.append(line)
    
    # Combine the lines into a single response
    user_response = '\n'.join(lines)
    
    return user_response