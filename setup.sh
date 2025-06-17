set -e

echo "Starting TinyLlama with Ollama..."
ollama run tinyllama:1.1b &
OLLAMA_PID=$!
sleep 10 

echo "Populating Qdrant with embeddings..."
python3.12 database/qdrant/setup_qdrant.py

echo "Setting up SQLite database..."
if [ -f database/sqlite/setup_sql.py ]; then
    python3.12 database/sqlite/setup_sql.py
else
    echo "Warning: database/sqlite/setup_sql.py not found. Skipping SQLite setup."
fi

echo "Setup complete."
