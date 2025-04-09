from mcp import ClientSession
from mcp.client.sse import sse_client
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Groq API key from environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables")

async def run():
    async with sse_client(url="http://localhost:8000/sse") as streams:
        async with ClientSession(*streams) as session:
            await session.initialize()

            # List available tools
            tools_response = await session.list_tools()
            available_tools = []
            if hasattr(tools_response, 'tools') and tools_response.tools:
                available_tools = [tool.name for tool in tools_response.tools]
            
            print("\n=== Todoist MCP Client ===")
            print("Available tools:", available_tools)
            print("Type 'exit' to quit")
            print("\nYou can ask to create tasks or view your tasks in natural language.")
            print("Examples:")
            print("- Create a task to buy groceries tomorrow")
            print("- Show me my tasks for today")
            print("- Add high priority task finish report by Friday")
            
            while True:
                # Get user input
                user_input = input("\nEnter your request: ")
                
                if user_input.lower() == 'exit':
                    print("Exiting...")
                    break
                
                # Call the unified todoist_assistant tool with the user's prompt
                if "todoist_assistant" in available_tools:
                    try:
                        result = await session.call_tool("todoist_assistant", arguments={"prompt": user_input})
                        if hasattr(result, 'content') and result.content:
                            print("\nTodoist Result:")
                            print("--------------")
                            print(result.content[0].text)
                            print("--------------")
                        else:
                            print("Error: No response content received from the server.")
                    except Exception as e:
                        print(f"Error calling Todoist assistant: {str(e)}")
                else:
                    print("Error: The todoist_assistant tool is not available on the server.")


if __name__ == "__main__":
    asyncio.run(run())