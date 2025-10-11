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
from fastapi.responses import JSONResponse
from NETwork.backend.handlers.handler_agent_conversation import AgentConversationHandler

# Load environment variable for allowed origins
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")

# Initialize FastAPI app
app = FastAPI()

# Allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Create post endpoint for agent conversation
@app.post("/api/generate_response")
async def generate_response(request: Request):
    try:
        # Create an instance of the handler
        handler = AgentConversationHandler()
        # Get data elements from request
        data = await request.json()
        contents = data["contents"]
        thread = data.get("thread_id")
        # Call the agent conversation function
        response, thread = handler.agent_conversation(contents, thread=thread)
        return {"response": response, "thread_id": getattr(thread, "id", None)}
    except Exception as e:
        import traceback
        print("Error in /api/generate_response:", e)
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
