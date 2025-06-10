import asyncio
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.openai import OpenAI
from llama_index.tools.mcp import (
    aget_tools_from_mcp_url,
)
import os
from dotenv import load_dotenv
import httpx

load_dotenv()

MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:9000/mcp")

async def get_oauth_token():
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "http://oauth-server:3000/token",
            data={
                "grant_type": "client_credentials",
                "client_id": "agent-1",
                "client_secret": "b1c2fb5c-5601-4a4f-89e2-e66707e7a4dd"
            }
        )
        resp.raise_for_status()
        return resp.json()["access_token"]

def wrap_tool_with_auth(tool, token):
    orig_fn = tool.fn
    async def wrapped_fn(*args, **kwargs):
        # Patch the tool's HTTP call to include the Authorization header
        if hasattr(tool, 'mcp_url'):
            # If the tool uses httpx, pass headers
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {token}"}
                # Assume POST with JSON body for generality
                resp = await client.post(tool.mcp_url, json=kwargs, headers=headers)
                resp.raise_for_status()
                return resp.json()
        # fallback to original
        return await orig_fn(*args, **kwargs)
    tool.fn = wrapped_fn
    return tool

async def main(user_query):
    token = await get_oauth_token()
    tools = await aget_tools_from_mcp_url(MCP_SERVER_URL)
    # Wrap each tool to inject the token
    tools = [wrap_tool_with_auth(tool, token) for tool in tools]
    agent = FunctionAgent(
        tools=tools,
        llm=OpenAI(model="gpt-4o-mini"),
        system_prompt="You are a helpful assistant with access to a SQLite database via MCP tools."
    )
    response = await agent.run(user_query)
    print(str(response))

if __name__ == "__main__":
    user_query = input("Enter your query: ")
    asyncio.run(main(user_query))
