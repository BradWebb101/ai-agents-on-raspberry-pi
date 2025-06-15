from agents.base_agent import BaseAgent
from agents.events import Event, Context, QuestionEvent, AgentResponseEvent, LogEvent
import asyncio
from typing import Dict, Any
from qdrant_client import QdrantClient
import logging
import os
from openai import OpenAI
from dotenv import load_dotenv

class ScienceAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="ScienceAgent")
        self.logger = logging.getLogger("ScienceAgent")
        self.system_prompt = (
            "You are a precise and logical science expert. "
            "You answer questions with scientific facts, evidence, and clear explanations. "
            "You enjoy debating scientific theories, discoveries, and the scientific method."
        )
        self.collection_name = "melvis_science"
        self.client = QdrantClient(host="localhost", port=6333)
        load_dotenv()
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def handle_event(self, event: Event, context: Context):
        if isinstance(event, QuestionEvent):
            context.add_event(LogEvent(sender=self.name, msg=f"Received question: {event.question}"))
            # Simulate thinking
            await asyncio.sleep(0.5)
            response = f"From a scientific perspective: {event.question} (analyzed empirically)"
            response_event = AgentResponseEvent(sender=self.name, response=response, agent_name=self.name)
            context.add_event(response_event)
            return response_event
        return None

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        question = task.get("data", "")
        self.logger.info(f"Received question: {question}")
        response = self.openai_client.embeddings.create(
            input=question,
            model="text-embedding-ada-002"
        )
        query_vector = response.data[0].embedding
        hits = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=3
        )
        if hits:
            answer = hits[0].payload.get("text", "No answer found.")
            self.logger.info(f"Answering: {answer}")
            return {"result": answer}
        self.logger.info("No answer found in the science vector database.")
        return {"result": "No answer found in the science vector database."} 