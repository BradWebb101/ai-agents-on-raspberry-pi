from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

from qdrant_client import QdrantClient
import random
import os


class PhilosophyAgent():
    def __init__(self, mock_rag=False):
        self.name = 'PhilosophyAgent'
        self.system_prompt = 'You are a helpful Philosophy agent'
        self.mock_rag = mock_rag
        self.agent = FunctionAgent(
            name=self.name,
            description='Handles philosophical queries and debates, providing thoughtful and reflective responses.',
            llm=Ollama(model="tinyllama"),
            system_prompt=self.system_prompt
        )
        self.qdrant_client = QdrantClient(host="localhost", port=6333, timeout=60)

    def run(self, user_query):
        try:
            if self.mock_rag:
                # Load and select a random paragraph from freewill_philosophy.txt
                data_path = os.path.join(os.path.dirname(__file__), '../database/qdrant/data/freewill_philosophy.txt')
                with open(data_path, 'r') as f:
                    text = f.read()
                paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
                database_context = random.choice(paragraphs) if paragraphs else '[MOCK RAG DATA]'
            else:
                print(f"PhilosophyAgent is searching the database with query: {user_query}")
                hits = self.qdrant_client.search(
                    collection_name="philosophy",
                    query_vector=[random.random() for _ in range(2)],
                    limit=1,
                    timeout=60
                )
                if not hits:
                    print("[ERROR] No hits found in the database.")
                    return "No relevant data found in the database."
                database_context = " | ".join([hit.payload.get("text", "") for hit in hits])

            print(f"PhilosophyAgent is running with query: {user_query}")
            response = self.agent.llm.complete(f"{user_query}. Context: {database_context}")
            return response
        except Exception as e:
            print(f"[ERROR] PhilosophyAgent encountered an error: {e}")
            return "Error occurred while processing the query."

