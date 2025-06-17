import asyncio
from supervisor_agent import SupervisorAgent
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def main(initial_prompt):
    supervisor = SupervisorAgent()
    print(f"Initial prompt: {initial_prompt}")
    await supervisor.orchestrate_debate(initial_prompt)

if __name__ == "__main__":
    initial_prompt = input("Enter the initial prompt for the Agent Supervisor: ")
    asyncio.run(main(initial_prompt))