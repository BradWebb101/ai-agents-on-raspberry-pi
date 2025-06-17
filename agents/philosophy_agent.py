from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

from qdrant_client import QdrantClient
import random
import os
import time

class PhilosophyAgent():
    def __init__(self, mock_rag=False):
        self.name = 'PhilosophyAgent'
        self.system_prompt = 'You are a helpful Philosophy agent'
        self.mock_rag = mock_rag
        self.agent = FunctionAgent(
            name=self.name,
            description='Handles philosophical queries and debates, providing thoughtful and reflective responses.',
            llm=Ollama(model="tinyllama", request_timeout=120.0),
            system_prompt=self.system_prompt
        )
        self.qdrant_client = QdrantClient(host="localhost", port=6333, timeout=60)

        self.ollama_embedding = OllamaEmbedding(
            model_name="nomic-embed-text",
            base_url="http://localhost:11434",
            ollama_additional_kwargs={"mirostat": 0},
        )

    def run(self, user_query):
        try:
            print(f"PhilosophyAgent is searching the database with query: {user_query}")
            hits = self.qdrant_client.search(
                collection_name="philosophy",
                query_vector=self.ollama_embedding.get_query_embedding(user_query),
                limit=1,
                timeout=60
            )
            if not hits:
                print("[ERROR] No hits found in the database.")
                return "No relevant data found in the database."
            database_context = " | ".join([hit.payload.get("text", "") for hit in hits])

            print(f"PhilosophyAgent is running with query: {user_query} + {database_context}")
            response = self.agent.llm.complete(f"{user_query}. Context: {database_context}")
            print('Response from PhilosophyAgent')
            print(response)
            return response
        except Exception as e:
            print(f"[ERROR] PhilosophyAgent encountered an error: {e}")
            return "Error occurred while processing the query."

