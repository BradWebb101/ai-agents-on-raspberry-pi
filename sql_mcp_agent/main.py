import asyncio
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.openai import OpenAI
from llama_index.tools.mcp import (
    aget_tools_from_mcp_url,
)
import os
from dotenv import load_dotenv

load_dotenv()

MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:9000/mcp")

async def main():
    tools = await aget_tools_from_mcp_url(MCP_SERVER_URL)
    agent = FunctionAgent(
        tools=tools,
        llm=OpenAI(model="gpt-4o-mini"),
        system_prompt="You are a helpful assistant with access to a SQLite database via MCP tools."
    )
    while True:
        user_query = input("Enter your query (or type 'exit' to quit): ")
        if not user_query or user_query.strip().lower() == 'exit':
            print("Exiting.")
            break
        response = await agent.run(user_query)
        print(str(response))

if __name__ == "__main__":
    asyncio.run(main())
