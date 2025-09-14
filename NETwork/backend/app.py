"""
This script sets up a FastAPI application for the NETwork project.

- Enables CORS to allow requests from the frontend (e.g., http://localhost:3000).
- Imports and uses the agent_conversation handler for processing chat requests.
- Exposes a POST endpoint at /api/agent that receives JSON data from the frontend,
  passes it to the agent_conversation function, and returns the response.
"""

# Example FastAPI app
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from handlers.handler_agent_conversation import agent_conversation

# Initialize FastAPI app
app = FastAPI()

# Allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/api/generate_response")
async def generate_response(request: Request):
    data = await request.json()
    # data['contents'] should be a list of {role, content}
    response, thread = agent_conversation(data["contents"])
    return {"response": response, "thread_id": thread.id}
