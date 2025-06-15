import os
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)

def get_openai_embedding(client, text):
    response = client.embeddings.create(input=text, model="text-embedding-ada-002")
    return response.data[0].embedding

def setup_qdrant_with_data():
    load_dotenv()
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    qdrant_client = QdrantClient(host="localhost", port=6333)
    data_dir = os.path.join(os.path.dirname(__file__), '../database/qdrant/data')
    file_to_collection = {
        "consciousness_philosophy.txt": "melvis_philosophy",
        "consciousness_science.txt": "melvis_science",
        "freewill_philosophy.txt": "melvis_philosophy",
        "freewill_science.txt": "melvis_science",
    }
    for filename in os.listdir(data_dir):
        if filename.endswith(".txt"):
            collection = file_to_collection.get(filename)
            if not collection:
                continue
            # Check if collection has data
            try:
                count = qdrant_client.count(collection_name=collection).count
                if count > 0:
                    logging.info(f"Collection {collection} already has data, skipping.")
                    continue
            except Exception:
                pass  # Collection may not exist yet
            file_path = os.path.join(data_dir, filename)
            with open(file_path, "r") as f:
                text = f.read()
            # Split into paragraphs
            chunks = [chunk.strip() for chunk in text.split('\n\n') if chunk.strip()]
            # Create collection
            qdrant_client.recreate_collection(
                collection_name=collection,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
            )
            points = []
            for i, chunk in enumerate(chunks):
                embedding = get_openai_embedding(openai_client, chunk)
                points.append(PointStruct(id=i, vector=embedding, payload={"text": chunk}))
            qdrant_client.upsert(collection_name=collection, points=points)
            logging.info(f"Inserted {len(points)} points into {collection}")

if __name__ == "__main__":
    setup_qdrant_with_data() 