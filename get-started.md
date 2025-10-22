🛳️ Getting Started Guide
This guide explains how to set up and run the Cruise AI Agent project locally.

⸻

🚀 Prerequisites
Before starting, make sure you have the following installed:
	•	Python 3.10+
	•	Docker 
	•	pip (Python package manager)

⸻

🧱 Step 1 — Start MongoDB in Docker
The project requires a running MongoDB instance on port 27017.
You can start MongoDB using Docker:

```
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  mongo:latest
```

This will launch MongoDB locally and make it accessible at mongodb://localhost:27017.

⸻

⚙️ Step 2 — Create the Environment File

Create a file named .env in the project root with the following variables:

```
OPENAI_API_KEY=key
DB_HOST=db-ro-01-do-user-2290310-0.f.db.ondigitalocean.com
DB_PORT=25060
DB_NAME=db_cruise
DB_USER=llm_user
DB_PASSWORD=password
```

💡 Make sure to replace key and password with your actual credentials.

⸻

🧠 Step 3 — Create the Vector Database

Before running the AI agent, you need to initialize the vector database.
This process populates your ChromaDB collection with cruise data and embeddings.

This will create the vector database inside the ./chroma_data directory.


🤖 Step 4 — Test the AI Agent
Once the vector database is ready, you can test the AI agent.

