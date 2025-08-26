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

def main():
    # Get the connect agent
    connect_agent = project.agents.get_agent(os.getenv("AZURE_AI_FOUNDRY_CONNECT_AGENT_ID"))

    # Create project thread
    thread = project.agents.threads.create()
    print(f"Created thread, ID: {thread.id}")

    # Start agent conversation with user prompt input
    try:
        while True:
            content = input("Enter your prompt (type 'quit' to exit):\n")
            print() # Create a new line

            if content.strip().lower() == "quit":
                print("Exiting conversation.")
                break

            project.agents.messages.create(
            thread_id=thread.id,
            role="user",
            content=content
            )
            run = project.agents.runs.create_and_process(
                thread_id=thread.id,
                agent_id=connect_agent.id
            )
            if run.status == "failed":
                print(f"Run failed: {run.last_error}")
            else:
                messages = project.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
                for message in messages:
                    if message.text_messages:
                        print(f"{message.role}:\n{message.text_messages[-1].text.value}\n")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
