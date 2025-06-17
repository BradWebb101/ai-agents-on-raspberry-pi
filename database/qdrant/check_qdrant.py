from qdrant_client import QdrantClient
import logging

logging.basicConfig(level=logging.INFO)

def check_qdrant_collections():
    client = QdrantClient(host="localhost", port=6333)
    collections = client.get_collections().collections
    if not collections:
        print("No collections found in Qdrant.")
        return
    print(f"Collections found: {[c.name for c in collections]}")
    for collection in collections:
        name = collection.name
        try:
            count = client.count(collection_name=name).count
            print(f"Collection '{name}' has {count} points.")
            if count > 0:
                # Try to fetch a sample point
                results = client.search(
                    collection_name=name,
                    query_vector=[0.0]*50,  # Dummy vector, just to get some results
                    limit=1,
                    with_payload=True,
                    with_vectors=True
                )
                for hit in results:
                    print(f"Sample payload from '{name}': {hit.payload}")
                    print(f"Sample vector from '{name}': {hit.vector}")
        except Exception as e:
            print(f"Error checking collection '{name}': {e}")

if __name__ == "__main__":
    check_qdrant_collections()