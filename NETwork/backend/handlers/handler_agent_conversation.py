"""
Handler for interactive agent conversation using Azure AI Foundry.
- Authenticates with Azure using environment variables.
- Provides reusable functions to create a conversation thread and process user prompts.
- Can be imported and called by other scripts (e.g., FastAPI backend).
- Supports an interactive CLI for testing the conversation flow.
"""

from azure.ai.projects import AIProjectClient
from azure.identity import ClientSecretCredential
from azure.ai.agents.models import ListSortOrder
from dotenv import load_dotenv
import os

load_dotenv()

# Initialise credentials client
credential = ClientSecretCredential(
    tenant_id=os.getenv("AZURE_TENANT_ID"),
    client_id=os.getenv("AZURE_CLIENT_ID"),
    client_secret=os.getenv("AZURE_CLIENT_SECRET")
)

# Initialise AI foundry project client
project = AIProjectClient(
    credential=credential,
    endpoint=os.getenv("AZURE_AI_FOUNDRY_ENDPOINT")
)

def get_connect_agent():
    """Return the connect agent object."""
    return project.agents.get_agent(os.getenv("AZURE_AI_FOUNDRY_CONNECT_AGENT_ID"))

def create_thread():
    """Create and return a new conversation thread."""
    return project.agents.threads.create()

def get_thread(thread_id):
    """Return an existing conversation thread."""
    return project.agents.threads.get(thread_id)

def delete_thread(thread_id):
    """Delete an existing conversation thread."""
    print(f"\nDeleted thread, ID: {thread_id}\n")
    return project.agents.threads.delete(thread_id)

def delete_all_threads():
    """Delete all existing conversation threads, skipping missing ones."""
    threads = project.agents.threads.list()
    for thread in threads:
        if thread.id is not None:
            project.agents.threads.get(thread.id)
            delete_thread(thread.id)


def send_user_message(thread_id, messages):
    """
    Accepts a list of message dicts (with 'content' as string) or a single string.
    """
    # If a string, wrap as a single message dict
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]
    elif isinstance(messages, dict):
        # If a dict, wrap in a list
        messages = [messages]
    for msg in messages:
        content = msg.get("content")
        if not isinstance(content, str):
            content = str(content)
        project.agents.messages.create(
            thread_id=thread_id,
            role=msg.get("role", "user"),
            content=content
        )

def run_agent(thread_id, agent_id):
    """Run the agent and return the run object."""
    return project.agents.runs.create_and_process(
        thread_id=thread_id,
        agent_id=agent_id
    )

def get_thread_messages(thread_id):
    """Return all messages in the thread, ordered descending."""
    return project.agents.messages.list(thread_id=thread_id, order=ListSortOrder.DESCENDING)

def agent_conversation(messages, thread=None):
    """
    Process a single prompt with the agent and return the latest agent response.
    If no thread is provided, a new one is created.
    Returns (response_text, thread)
    """
    connect_agent = get_connect_agent()
    if thread is None:
        thread = create_thread()
        print(f"\nCreated thread, ID: {thread.id}\n")
    send_user_message(thread.id, messages)
    run = run_agent(thread.id, connect_agent.id)
    if run.status == "failed":
        return f"Run failed: {run.last_error}"
    else:
        messages = project.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
        response = None
        for message in messages:
            if message.text_messages:
                response = message.text_messages[-1].text.value
        return response, thread

def main():
    """Interactive CLI for agent conversation."""
    try:
        while True:
            content = input("Enter your prompt (type 'quit' to exit):\n")
            if len(content) == 0:
                continue
            if content.strip().lower() == "quit":
                print("Exiting conversation.")
                break
            if content.strip().lower() == "delete all":
                delete_all_threads()
                print("Deleted all conversation threads.")
                continue
            response, thread = agent_conversation(content)
            print(f"agent:\n{response}\n")
            print(f"Continuing conversation in thread ID: {thread.id}\n")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
