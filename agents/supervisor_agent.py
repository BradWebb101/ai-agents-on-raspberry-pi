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
    
    
    def run(self, user_query, context={}):
        try:
            response = self.agent.llm.complete(f"{user_query}. last debate response summary: {context}")
            print('Supervisor')
            print('='*20)
            print(response)
            return response
        except Exception as e:
            print(f"[ERROR] ScienceAgent encountered an error: {e}")
            return "Error occurred while processing the query."

    async def orchestrate_debate(self, question: str):
        """
        Orchestrate a debate between agents using AgentWorkflow.
        """
        print("Starting debate...")

        state = {
            "current_question": question,
            "debate_log": []
        }

        max_turns = 4
        turn_count = 0
        # Initialize the next agent name to alternate between PhilosophyAgent and ScienceAgent
        next_agent_name = random.choice(["PhilosophyAgent", 'ScienceAgent'])
        while turn_count < max_turns:
            next_agent = self.philosophy_agent if next_agent_name == "PhilosophyAgent" else self.science_agent
            if not isinstance(state["current_question"], str):
                state["current_question"] = str(state["current_question"])

            agent_context = state.get("agent_context", {})
            agent_response = await asyncio.to_thread(next_agent.run, state["current_question"], agent_context)
            state["debate_log"].append(f"{next_agent_name+'agent_response'+str(turn_count)}: {agent_response}")
            
            print(f'{next_agent.name} has a response')
            print('='*20)
            summary_agent_response = await asyncio.to_thread(self.summary_agent.run, agent_response)
            state["debate_log"].append(f"{next_agent_name+'agent_summary'+str(turn_count)}: {agent_response}")
            
            
            # Update the current question with the summarized response
            state["current_question"] = summary_agent_response
            state["agent_context"] = agent_context

            # Alternate the next agent name
            next_agent_name = "ScienceAgent" if next_agent_name == "PhilosophyAgent" else "PhilosophyAgent"

            # # Add a 35% chance for the moderator to jump in with a clarifying question
            # if random.random() < 0.20:
                
            #     random_additions = random.choice([
            #     "Let's keep the discussion focused and respectful.",
            #     "Can we explore that idea further?",
            #     "Please clarify your argument for the audience."
            #     ])
            #     clarifying_question = random_additions
            #     print("Moderator jumps in with a clarifying question.")
            #     print('='*20)
            #     print('clarifying_question')
            #     agent_response = await asyncio.to_thread(next_agent.run, clarifying_question, agent_context)
            #     summary_agent_response = await asyncio.to_thread(self.summary_agent.run, agent_response)

            #     state["debate_log"].append(f"Moderator: {clarifying_question}")
            #     state["debate_log"].append(f"{next_agent_name}: {agent_response}")
            #     state["current_question"] = summary_agent_response
            #     state["agent_context"] = agent_context
            #     turn_count += 1
            #     print('='*20)
            #     continue

            turn_count += 1
            print('='*20)

        # Generate a UUID for the filename
        file_uuid = str(uuid.uuid4())
        file_path = f"../debate_logs/{file_uuid}.txt"

        # Write the debate log to the file
        with open(file_path, "w") as log_file:
            for log in state["debate_log"]:
                log_file.write(log + "\n")

        print(f"Debate log saved to {file_path}")
