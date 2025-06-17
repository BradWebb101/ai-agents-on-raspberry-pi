import asyncio
from supervisor_agent import SupervisorAgent
import sys
import os
import argparse
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set USE_QDRANT=0 or USE_QDRANT=false to disable Qdrant RAG database in all agents.
# Default is to use Qdrant if the variable is not set.

async def main(initial_prompt, mock_rag=False):
    supervisor = SupervisorAgent(mock_rag=mock_rag)
    print(f"Initial prompt: {initial_prompt}")
    await supervisor.orchestrate_debate(initial_prompt)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--mock-rag', action='store_true', help='Use mock RAG instead of real database')
    args = parser.parse_args()
    initial_prompt = input("Enter the initial prompt for the Agent Supervisor: ")
    asyncio.run(main(initial_prompt, mock_rag=args.mock_rag))