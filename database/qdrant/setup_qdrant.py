import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance
from dotenv import load_dotenv
import logging
from llama_index.embeddings.ollama import OllamaEmbedding
import uuid
import random

logging.basicConfig(level=logging.INFO)

def get_ollama_embedding(ollama_embedding, text):
    return ollama_embedding.get_query_embedding(text)

def setup_qdrant_with_data():
    load_dotenv()
    qdrant_client = QdrantClient(host="localhost", port=6333)
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    file_to_collection = {
        # "consciousness_philosophy.txt": "philosophy",
        # "consciousness_science.txt": "science",
        "freewill_philosophy.txt": "philosophy",
        "freewill_science.txt": "science",
    }
    for filename in os.listdir(data_dir):
        if filename.endswith(".txt"):
            collection = file_to_collection.get(filename)
            if not collection:
                continue
            # Check if collection exists
            try:
                qdrant_client.get_collection(collection_name=collection)
            except Exception:
                # Create collection if it doesn't exist
                qdrant_client.recreate_collection(
                    collection_name=collection,
                    vectors_config=VectorParams(size=2, distance=Distance.COSINE)
                )
            file_path = os.path.join(data_dir, filename)
            with open(file_path, "r") as f:
                text = f.read()
            # Split into paragraphs
            chunks = [chunk.strip() for chunk in text.split('\n\n') if chunk.strip()]
            points = []
            for i, chunk in enumerate(chunks):
                point_id = str(uuid.uuid4())  # Convert UUID to string for valid PointStruct ID
                points.append(PointStruct(id=point_id, vector=[random.random() for _ in range(2)], payload={"text": chunk}))
            qdrant_client.upsert(collection_name=collection, points=points)
            logging.info(f"Inserted {len(points)} points into {collection}")

if __name__ == "__main__":
    setup_qdrant_with_data()