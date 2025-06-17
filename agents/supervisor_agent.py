from llama_index.core.agent.workflow import AgentWorkflow, FunctionAgent
from llama_index.embeddings.ollama import OllamaEmbedding
from qdrant_client import QdrantClient
from dotenv import load_dotenv
from llama_index.llms.ollama import Ollama
from philosophy_agent import PhilosophyAgent
from science_agent import ScienceAgent
from summary_agent import SummaryAgent
import asyncio
import uuid
import random

class SupervisorAgent:
    def __init__(self, mock_rag=False):
        load_dotenv()
        self.qdrant_client = QdrantClient(host="localhost", port=6333)

        self.philosophy_agent = PhilosophyAgent(mock_rag=mock_rag)
        self.science_agent = ScienceAgent(mock_rag=mock_rag)
        self.summary_agent = SummaryAgent()

        self.supervisor_agent = FunctionAgent(
            name="SupervisorAgent",
            llm=Ollama(model="tinyllama", request_timeout=120.0),
            description="Moderates debates and summarizes outcomes.",
            system_prompt="You are a neutral debate moderator.",
            can_handoff_to=["PhilosophyAgent", "ScienceAgent"]
        )

    async def orchestrate_debate(self, question: str):
        """
        Orchestrate a debate between agents using AgentWorkflow.
        """
        print("Starting debate...")

        state = {
            "current_question": question,
            "debate_log": []
        }

        max_turns = 10
        turn_count = 0
        # Initialize the next agent name to alternate between PhilosophyAgent and ScienceAgent
        next_agent_name = random.choice(["PhilosophyAgent", 'ScienceAgent'])
        while turn_count < max_turns:
            next_agent = self.philosophy_agent if next_agent_name == "PhilosophyAgent" else self.science_agent
            print((f"{next_agent.name} has been proposed the question {state['current_question']}"))
            if not isinstance(state["current_question"], str):
                state["current_question"] = str(state["current_question"])

            context = {}

            agent_response = await asyncio.to_thread(next_agent.run, state["current_question"], context)
            state["debate_log"].append(f"{next_agent_name+'agent_response'+str(turn_count)}: {agent_response}")
            print('Summary Agent got asked to summarise')
            summary_agent_response = await asyncio.to_thread(self.summary_agent.run, agent_response)
            state["debate_log"].append(f"{next_agent_name+'agent_summary'+str(turn_count)}: {summary_agent_response}")
            
            context = summary_agent_response
            # Alternate the next agent name
            next_agent_name = "ScienceAgent" if next_agent_name == "PhilosophyAgent" else "PhilosophyAgent"

            turn_count += 1

        # Generate a UUID for the filename
        file_uuid = str(uuid.uuid4())
        file_path = f"../debate_logs/{file_uuid}.txt"

        # Write the debate log to the file
        with open(file_path, "w") as log_file:
            for log in state["debate_log"]:
                log_file.write(log + "\n")

        print(f"Debate log saved to {file_path}")
