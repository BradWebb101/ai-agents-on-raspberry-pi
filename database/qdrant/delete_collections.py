from qdrant_client import QdrantClient
import logging

logging.basicConfig(level=logging.INFO)

def delete_all_collections():
    client = QdrantClient(host="localhost", port=6333)
    collections = client.get_collections().collections
    if not collections:
        print("No collections found in Qdrant.")
        return
    print(f"Deleting collections: {[c.name for c in collections]}")
    for collection in collections:
        try:
            client.delete_collection(collection_name=collection.name)
            print(f"Deleted collection '{collection.name}'.")
        except Exception as e:
            print(f"Error deleting collection '{collection.name}': {e}")

if __name__ == "__main__":
    delete_all_collections()