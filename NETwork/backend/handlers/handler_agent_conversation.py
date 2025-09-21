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

class AgentConversationHandler:
    def __init__(self):
        self.ListSortOrder = ListSortOrder
        self.credential = ClientSecretCredential(
            tenant_id=os.getenv("AZURE_TENANT_ID"),
            client_id=os.getenv("AZURE_CLIENT_ID"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET")
        )
        self.project = AIProjectClient(
            credential=self.credential,
            endpoint=os.getenv("AZURE_AI_FOUNDRY_ENDPOINT")
        )
        self.connect_agent_id = os.getenv("AZURE_AI_FOUNDRY_CONNECT_AGENT_ID")

    def get_connect_agent(self):
        return self.project.agents.get_agent(self.connect_agent_id)

    def create_thread(self):
        return self.project.agents.threads.create()

    def get_thread(self, thread_id):
        return self.project.agents.threads.get(thread_id)

    def delete_thread(self, thread_id):
        print(f"\nDeleted thread, ID: {thread_id}\n")
        return self.project.agents.threads.delete(thread_id)

    def delete_all_threads(self):
        threads = self.project.agents.threads.list()
        for thread in threads:
            if thread.id is not None:
                try:
                    self.project.agents.threads.get(thread.id)
                    self.delete_thread(thread.id)
                except Exception as e:
                    if "No thread found with id" in str(e):
                        continue
                    else:
                        print(f"Error deleting thread {thread.id}: {e}")

    def send_user_message(self, thread_id, messages):
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        elif isinstance(messages, dict):
            messages = [messages]
        for msg in messages:
            content = msg.get("content")
            if not isinstance(content, str):
                content = str(content)
            self.project.agents.messages.create(
                thread_id=thread_id,
                role=msg.get("role", "user"),
                content=content
            )

    def run_agent(self, thread_id, agent_id):
        return self.project.agents.runs.create_and_process(
            thread_id=thread_id,
            agent_id=agent_id
        )

    def get_thread_messages(self, thread_id):
        return self.project.agents.messages.list(thread_id=thread_id, order=self.ListSortOrder.DESCENDING)

    def agent_conversation(self, messages, thread=None):
        connect_agent = self.get_connect_agent()
        if thread is None:
            thread = self.create_thread()
            print(f"\nCreated new thread, ID: {thread.id}\n")
        elif isinstance(thread, str):
            thread = self.get_thread(thread)
            print(f"\nUsing existing thread, ID: {thread.id}\n")

        self.send_user_message(thread.id, messages)
        run = self.run_agent(thread.id, connect_agent.id)
        if run.status == "failed":
            return f"Run failed: {run.last_error}", thread
        else:
            messages = self.project.agents.messages.list(thread_id=thread.id, order=self.ListSortOrder.ASCENDING)
            response = None
            for message in messages:
                if message.text_messages:
                    response = message.text_messages[-1].text.value
            return response, thread

def main():
    """Interactive CLI for agent conversation."""
    try:
        handler = AgentConversationHandler()
        thread = None
        while True:
            content = input("Enter your prompt (type 'quit' to exit):\n")
            if len(content) == 0:
                continue
            if content.strip().lower() == "quit":
                print("Exiting conversation.")
                break
            if content.strip().lower() == "delete all":
                handler.delete_all_threads()
                print("Deleted all conversation threads.")
                thread = None
                continue
            response, thread = handler.agent_conversation(content, thread=thread)
            print(f"agent:\n{response}\n")
            print(f"Continuing conversation in thread ID: {thread.id}\n")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
