import asyncio
import logging
from supervisor_agent import AgentSupervisor

# Suppress httpx and OpenAI HTTP request logging
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)

logging.basicConfig(level=logging.INFO)

async def main():
    supervisor = AgentSupervisor()
    while True:
        protocol = input("Choose protocol (classic/a2a, or 'exit' to quit): ").strip().lower()
        if protocol == 'exit':
            print("Exiting debate system. Goodbye!")
            break
        question = input("Enter the debate question: ")
        if protocol == 'a2a':
            await supervisor.run_debate_a2a(question)
        else:
            await supervisor.run_debate(question)

if __name__ == "__main__":
    asyncio.run(main()) 