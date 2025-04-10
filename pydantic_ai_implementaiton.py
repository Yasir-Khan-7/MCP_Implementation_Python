from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider
from pydantic_ai.mcp import  MCPServerStdio

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key from the environment
api_key = os.getenv('GROQ_API_KEY')

model = GroqModel(
    'qwen-2.5-32b', provider=GroqProvider(api_key=api_key)
)
fetchserver = MCPServerStdio('python', ["-m", "mcp_server_fetch"])


agent = Agent(model, instrument=True,mcp_servers=[fetchserver])

async def main():
    async with agent.run_mcp_servers():
        result = await agent.run("hello")
        while True:
            print(f"\n{result.data}")
            user_input = input("Enter a message: ")
            result = await agent.run(user_input,
                                    message_history = result.new_messages()
                                    )
        

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())