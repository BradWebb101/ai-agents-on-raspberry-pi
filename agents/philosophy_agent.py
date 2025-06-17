from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

from qdrant_client import QdrantClient
import random


class PhilosophyAgent():
    def __init__(self):
        self.name = 'PhilosophyAgent'
        self.system_prompt = 'You are a helpful Philosophy agent'
        self.agent = FunctionAgent(
            name=self.name,
            description='Handles philosophical queries and debates, providing thoughtful and reflective responses.',
            llm=Ollama(model="tinyllama"),
            system_prompt=self.system_prompt
        )
        self.qdrant_client = QdrantClient(host="localhost", port=6333, timeout=60)

    def run(self, user_query, context={}):
        try:
            print(f"PhilosophyAgent is searching the database with query: {user_query}")
            hits = self.qdrant_client.search(
                collection_name="philosophy",
                query_vector=[random.random() for _ in range(10)],
                limit=1,
                timeout=60
            )
            if not hits:
                print("[ERROR] No hits found in the database.")
                return "No relevant data found in the database."

            database_context = " | ".join([hit.payload.get("text", "") for hit in hits])

            # Combine user query, database context, and additional context
            response = self.agent.llm.complete(f"{user_query}. Context: {database_context}. Additional Context: {context}")
            print(response)
            return response
        except Exception as e:
            print(f"[ERROR] PhilosophyAgent encountered an error: {e}")
            return "Error occurred while processing the query."

