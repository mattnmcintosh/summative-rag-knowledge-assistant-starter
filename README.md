Summative RAG Knowledge Assistant
Project Description
A local Retrieval-Augmented Generation (RAG) application that combines a Python Flask backend, a persistent ChromaDB vector store, local LLMs running via Ollama, and a React frontend. The application enables users to query a private knowledge base and receive accurate, context-grounded answers along with supporting source citations.

User Need or Scenario
With new and current employees, there might be a time where an employee may not be familiar with all the guidelines and domain knowledge endemic to their work environment. Instead of asking another busy employee for help, they
can ask an AI assistant under the RAG model. This allows for a specific focus on the knowledge base of the corporate domain, gives the ability to show the source material so the employee can check them for more knowledge (which also
helps minimize repeat requests since the employee now knows where to find the knowledge), and allows this in a dialogue based interface which is more intuitive than a command-based system.

Installation Instructions
Clone or download the project repository to your local machine.

Open your terminal and navigate into the server directory.

Install the required Python dependencies by running the following command:
pipenv install

Activate your virtual environment:
pipenv shell

Navigate to the client directory and install frontend dependencies:
npm install

Run Instructions
Start your local Ollama desktop application or background service.

Seed your vector database by running the data ingestion script:
pipenv run python seed.py

Start the Flask backend server from the server directory:
pipenv run python app.py

Start the React frontend client from the client directory:
npm run dev

Open your browser and navigate to the local client URL provided by Vite.

Required Environment Variables
Create a configuration file named .env inside your server directory with the following variables:

OLLAMA_BASE_URL: The endpoint URL for your local Ollama instance (default: http://localhost:11434).

GENERATION_MODEL: The local model used for generating answers (default: llama3.2).

EMBEDDING_MODEL: The local model used for creating embeddings (default: nomic-embed-text).

CHROMA_PATH: The local storage path for the persistent Chroma database (default: ./chroma_db).

COLLECTION_NAME: The name of the Chroma collection (default: knowledge_assistant).

KNOWLEDGE_BASE_PATH: The path to your source documents folder (default: ./knowledge_base).

TOP_K: The number of relevant chunks retrieved per query (default: 3).

TEMPERATURE: The generation model temperature setting (default: 0.2).

FLASK_DEBUG: Enables or disables Flask debug mode (default: True).

CLIENT_ORIGIN: The allowed origin URL for frontend CORS policy (default: http://localhost:5173).

API Route Descriptions
GET /api/health: Confirms that the backend service is running and responsive. Returns a status message.

POST /api/ask: Receives a JSON payload containing a user question, processes it through the RAG retrieval and generation pipeline, and returns a JSON response containing the generated answer string and an array of supporting source excerpts.

Description of the RAG Workflow
Browser > React frontend > Sent to /api/ask > Calling answer_question in app > retriving relevant chunks by creating an embedding and querying the chroma database in vector_store, returning the top k > builds the prompt with the relevant chunks in rag_service > calls the actual AI API with the data from the query and the prompt > returns the AI answer and sources to the API > formats it as JSON > returns it to the React frontend > which is then formatted in a user friendly manner in the browser 

| Sample Question | Was the Answer Relevant? | Were Useful Sources Returned? | Notes |
I am trying to onboard but I cannot access one of the tools I am required to use. How do I fix this? | Yes | Yes | This question was targeted to prioritize that all steps in the employee onboarding for having access trouble were given back to the user. It scored the support guide as top 3 but weak, most likely because I was narrowing down on a small piece of information and it found the target information in 2 chunks, leading to a low scoring third source.

What should a customer do if they are having trouble? | Not really | Not really | I tried a more vague one this time, and it had some trouble as expected. It assumed the problem was a login and hallucinated that customers had access to internal tools. If queries to the AI were expected to be this vague in the workplace, then it could possibly be improved on, either with knowledge base content or model refinement.

What should the employee do if they clicked a suspicious link without due caution first? | Yes | Yes | I was trying to narrow in on something specific and realistic this time using the kind of query I would personally use. The model performed well and returned the correct sources.

Known Limitations and Future Improvements
Local Hardware Dependency: Performance depends heavily on the local machine hardware and available GPU memory when running Ollama models.

Static Knowledge Base: Document ingestion currently requires manual re-seeding when source files are updated.

Future Improvements: Add automated file watcher syncing for live knowledge base updates, support for multi-turn conversational history, and advanced semantic chunking strategies.