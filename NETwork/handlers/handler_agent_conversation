from azure.ai.projects import AIProjectClient
from azure.identity import ClientSecretCredential
from azure.ai.agents.models import ListSortOrder
from dotenv import load_dotenv
import os

load_dotenv()

TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
PROJECT_ENDPOINT = os.getenv("AZURE_AI_FOUNDRY_ENDPOINT")
CONNECT_AGENT_ID = os.getenv("AZURE_AI_FOUNDRY_CONNECT_AGENT_ID")

credential = ClientSecretCredential(
    tenant_id=TENANT_ID,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

project = AIProjectClient(
    credential=credential,
    endpoint=PROJECT_ENDPOINT
)


connect_agent = project.agents.get_agent(CONNECT_AGENT_ID)


thread = project.agents.threads.create()
print(f"Created thread, ID: {thread.id}")

message = project.agents.messages.create(
    thread_id=thread.id,
    role="user",
    content=
    """
    There are 11/8 odds of Keys, Rybakina and Svitolina all to win their 1st round matches at the US open in straight sets.

    Calculate and share your own betting odds. Is this a good bet?

    In a table, summarise each player's previous 5 matches across all tournaments. Make an assessment of their strengths and weeakness.

    What are the risks from a betting perspective if one of them plays a left handed player?

    Predict the outcome of their 1st round matches.

    Provide a betting strategy.
    """
)

run = project.agents.runs.create_and_process(
    thread_id=thread.id,
    agent_id=connect_agent.id)

if run.status == "failed":
    print(f"Run failed: {run.last_error}")
else:
    messages = project.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    for message in messages:
        if message.text_messages:
            print(f"{message.role}:\n{message.text_messages[-1].text.value}\n")
