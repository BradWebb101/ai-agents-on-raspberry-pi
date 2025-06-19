set -e

echo "Starting TinyLlama with Ollama..."
ollama run tinyllama &
OLLAMA_PID=$!
sleep 10 

ollama pull nomic-embed-text &
sleep 10 

echo "Populating Qdrant with embeddings..."
python database/qdrant/setup_qdrant.py

echo "Setting up SQLite database..."
if [ -f database/sqlite/setup_sql.py ]; then
    python database/sqlite/setup_sql.py
else
    echo "Warning: database/sqlite/setup_sql.py not found. Skipping SQLite setup."
fi

echo "Setup complete."
