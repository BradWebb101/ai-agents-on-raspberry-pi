# Engineering Day: Multi-Agent Debate System

## How to Run

1. **Create a Python 3.12 virtual environment:**

   ```sh
   python3.12 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   cd agents
   pip install -r requirements.txt
   ```

2. **Set your OpenAI API key (required for MCP server):**

   You must have an OpenAI API key to use the MCP server. Add it to your environment or a `.env` file:

   ```sh
   echo "OPENAI_API_KEY=************" >> .env
   ```

3. **Run the setup script:**

   ```sh
   bash setup.sh
   ```

   This will:
   - Start TinyLlama with Ollama
   - Populate Qdrant with embeddings
   - Set up the SQLite database (if setup_sql.py exists)

4. **Start all services with Docker Compose:**

   ```sh
   docker compose up --build
   ```

   This will build and start all containers as defined in `docker-compose.yml`.

---

## Overview

This project is a modular, multi-agent debate and evaluation system that leverages LLMs (primarily TinyLlama via Ollama) and a Qdrant vector database. It features agents for philosophy, science, and summarization, orchestrated by a supervisor agent, and supports SQL-based queries via an MCP server. The system is containerized for easy deployment.

---

## Directory Structure

- **agents/**: Core agent logic (Philosophy, Science, Summary, Supervisor, entrypoint)
- **database/qdrant/**: Qdrant vector DB setup, data, and scripts
- **database/sqlite/**: SQLite DB, API, and Dockerfile
- **evaluation/**: Scripts for evaluating agent conversations
- **mcp_server/**: FastAPI server for MCP (Multi-Component Protocol) tools
- **sql_mcp_agent/**: Agent for querying the MCP server using OpenAI
- **utils/**: Utility scripts (e.g., for generating dummy data)
- **docker-compose.yml**: Service orchestration (Qdrant, with templates for other services)
- **start.sh**: Script to build and start all services, and wait for readiness

---

## Agents

- **PhilosophyAgent**: Handles philosophical queries, uses TinyLlama via Ollama, retrieves context from Qdrant.
- **ScienceAgent**: Handles scientific queries, uses TinyLlama via Ollama, retrieves context from Qdrant.
- **SummaryAgent**: Summarizes responses in 5 words, uses TinyLlama.
- **SupervisorAgent**: Orchestrates debates, alternates between Philosophy and Science agents, and logs debates.
- **SQL MCP Agent**: Uses OpenAI to query the MCP server for SQL database access.

---

## Vector Database (Qdrant)

- **Setup**: See `database/qdrant/README.md` for details.
- **Data**: Text files in `database/qdrant/data/` are embedded and indexed.
- **Scripts**: 
  - `setup_qdrant.py`: Loads data and embeddings into Qdrant using TinyLlama via Ollama.
  - `delete_collections.py`: Removes collections from Qdrant.
  - `check_qdrant.py`: Health check for Qdrant.

---

## SQLite API

- **API**: FastAPI app in `database/sqlite/api.py`, containerized with its own Dockerfile.
- **Database**: `database.db` with e-commerce schema and dummy data (see `utils/main.py`).

---

## MCP Server

- **API**: FastAPI app in `mcp_server/mcp_server.py`, exposes endpoints for agent tools.
- **Requirements**: See `mcp_server/requirements.txt`.
- **Dockerfile**: Provided for containerized deployment.
- **Requires**: An OpenAI API key set as `OPENAI_API_KEY` in your environment or `.env` file.

---

## Evaluation

- **evaluation/main.py**: Runs a set of philosophical and scientific questions through the agents and saves the results.

---

## Utilities

- **utils/main.py**: Generates and populates the SQLite database with dummy e-commerce data.

---

## Running the System

### 1. Prerequisites

- **Docker** and **Docker Compose** installed
- **Ollama** installed and running locally
- **TinyLlama** model pulled for Ollama
- **OpenAI API Key** (required for MCP server)

  ```sh
  ollama run tinyllama:1.1b
  ```

  This will download and start the TinyLlama model, which is required for all agent LLM operations.

### 2. Start Services

- To start Qdrant (and optionally other services), use:

  ```sh
  docker-compose up -d
  ```

  Or use the provided script for a full startup and readiness check:

  ```sh
  ./start.sh
  ```

  This script will:
  - Build and start all containers
  - Wait for OIDC, SQLite API, and MCP server to be ready
  - (Optionally) run the agent debate orchestrator

### 3. Populate Qdrant

- Run the setup script to embed and load data into Qdrant:

  ```sh
  python database/qdrant/setup_qdrant.py
  ```

### 4. Run Agents

- **Main Debate Orchestrator**:

  ```sh
  python agents/main.py
  ```

- **SQL MCP Agent**:

  ```sh
  python sql_mcp_agent/main.py
  ```

- **Evaluation**:

  ```sh
  python evaluation/main.py
  ```

---

## Notes

- **Model**: All agents use TinyLlama via Ollama (`ollama run tinyllama:1.1b` must be running).
- **Qdrant**: Data is persisted in `database/qdrant/data/`.
- **Environment Variables**: Some scripts use `.env` for configuration. **You must set `OPENAI_API_KEY` to use the MCP server.**
- **Extensibility**: Add new agents or data by following the patterns in the `agents/` and `database/qdrant/` directories.

---

## References

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Ollama Documentation](https://ollama.com/)
- [LlamaIndex](https://github.com/jerryjliu/llama_index) 