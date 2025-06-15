# Qdrant Vector Database

This folder contains the configuration for running a Qdrant vector database as a Docker container for use as a vector store in your agent system.

## Usage

1. **Add to your `docker-compose.yml`:**

```yaml
services:
  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
    volumes:
      - ./qdrant/data:/qdrant/storage
    restart: unless-stopped
```

2. **Start Qdrant:**

```sh
docker-compose up -d qdrant
```

3. **Python Client Example:**

Install the client:

```
pip install qdrant-client
```

Example usage:

```python
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance
import numpy as np

client = QdrantClient(host="localhost", port=6333)
collection_name = "melvis_philosophy"

# Create collection (e.g., 384-dim vectors)
client.recreate_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)

# Add a point
vector = np.random.rand(384).tolist()
payload = {"question": "What is the meaning of life?", "answer": "42"}
point = PointStruct(id=1, vector=vector, payload=payload)
client.upsert(collection_name=collection_name, points=[point])

# Search
results = client.search(
    collection_name=collection_name,
    query_vector=vector,
    limit=3
)
for hit in results:
    print(hit.payload)
```

## Data Persistence

- The `./qdrant/data` directory is mounted as a volume to persist your vector data.

## Documentation

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Qdrant Python Client](https://qdrant.github.io/qdrant/redoc/index.html) 