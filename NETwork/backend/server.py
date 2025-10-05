"""
This script sets up a FastAPI application for the NETwork project.

- Entry point for running the FastAPI backend server.
- Enables CORS to allow requests from the frontend (e.g., http://localhost:3000).
- Imports and uses the agent_conversation handler for processing chat requests.
- Exposes a POST endpoint at /api/agent that receives JSON data from the frontend,
  passes it to the agent_conversation function, and returns the response.
"""

# Example FastAPI app
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from NETwork.backend.handlers.handler_agent_conversation import AgentConversationHandler

# Load environment variable for allowed origins
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")

# Initialize FastAPI app
app = FastAPI()

# Allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://ambitious-water-00b340403.1.azurestaticapps.net"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/api/generate_response")
async def generate_response(request: Request):
    data = await request.json()
    handler = AgentConversationHandler()
    contents = data["contents"]
    thread = data.get("thread_id")
    response, thread = handler.agent_conversation(contents, thread=thread)
    return {"response": response, "thread_id": thread.id}
