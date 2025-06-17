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
    def __init__(self):
        load_dotenv()
        self.qdrant_client = QdrantClient(host="localhost", port=6333)

        self.philosophy_agent = PhilosophyAgent() 
        self.science_agent = ScienceAgent() 
        self.summary_agent = SummaryAgent()

        self.supervisor_agent = FunctionAgent(
            name="SupervisorAgent",
            llm=Ollama(model="tinyllama"),
            description="Moderates debates and summarizes outcomes.",
            system_prompt="You are a neutral debate moderator.",
            can_handoff_to=["PhilosophyAgent", "ScienceAgent"]
        )

        # Setup workflow
        self.workflow = AgentWorkflow(
            agents=[self.philosophy_agent.agent, self.science_agent.agent, self.supervisor_agent],
            root_agent=self.supervisor_agent.name,
            initial_state={
                "research_notes": {},
                "debate_summary": "No summary yet."
            }
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

        max_turns = 6
        turn_count = 0

        while turn_count < max_turns:
            print(f"Turn {turn_count + 1}: SupervisorAgent moderates")

            next_agent_name = random.choice([self.philosophy_agent.name, self.science_agent.name])
            print(f"SupervisorAgent hands off to: {next_agent_name}")

            next_agent = self.philosophy_agent if next_agent_name == "PhilosophyAgent" else self.science_agent

            if not isinstance(state["current_question"], str):
                state["current_question"] = str(state["current_question"])

            agent_context = state.get("agent_context", {})
            agent_response = await asyncio.to_thread(next_agent.run, state["current_question"], agent_context)

            summary_agent_response = await asyncio.to_thread(self.summary_agent.run, agent_response)

            state["debate_log"].append(f"{next_agent_name}: {agent_response}")
            state["current_question"] = summary_agent_response
            state["agent_context"] = agent_context

            turn_count += 1
            print('='*20)

        # Generate a UUID for the filename
        file_uuid = str(uuid.uuid4())
        file_path = f"../debate_logs/{file_uuid}.txt"

        # Write the debate log to the file
        with open(file_path, "w") as log_file:
            log_file.write("\n--- Debate Summary ---\n")
            for log in state["debate_log"]:
                log_file.write(log + "\n")
            log_file.write("--- End of Debate ---\n")

        print(f"Debate log saved to {file_path}")
