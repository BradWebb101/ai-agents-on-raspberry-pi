import asyncio
from supervisor_agent import SupervisorAgent
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set USE_QDRANT=0 or USE_QDRANT=false to disable Qdrant RAG database in all agents.
# Default is to use Qdrant if the variable is not set.

async def main(initial_prompt):
    supervisor = SupervisorAgent()
    print(f"Initial prompt: {initial_prompt}")
    await supervisor.orchestrate_debate(initial_prompt)

if __name__ == "__main__":
    initial_prompt = input("Enter the initial prompt for the Agent Supervisor: ")
    asyncio.run(main(initial_prompt))