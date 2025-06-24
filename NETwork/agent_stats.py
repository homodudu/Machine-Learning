import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from data_handler import retrieve_github_tennis_stats

# Load environment variables from dotenv file
load_dotenv()

# Configure Azure OpenAI client
api_endpoint = "https://agentic-ai-23062025.cognitiveservices.azure.com/"
model_name = "gpt-4.1-mini"
deployment = "gpt-4.1-mini"

api_key = os.getenv("GPT4_MINI_API_KEY")
api_version = "2024-12-01-preview"

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=api_endpoint,
    api_key=api_key,
)

# Retrieve tennis statistics from GitHub and store locally
repo_atp = os.getenv("GITHUB_ATP_REPO")
repo_wta = os.getenv("GITHUB_WTA_REPO")
repo_list = {repo_atp, repo_wta}

for repo in repo_list:
    retrieve_github_tennis_stats(repo,2018)
    print(f"Data handler script executed successfully for repo: {repo}.")
