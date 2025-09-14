import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

# Load environment variables from .env file
load_dotenv()
REPO_LOCAL = os.getenv("LOCAL_REPO_BET")

# Azure Open AI settings
OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

# Initialise the azure blob service container client
BLOB_CONNECTION_STRING = os.getenv("AZURE_BLOB_CONNECTION_STRING")
BLOB_CONTAINER_NAME = os.getenv("AZURE_BLOB_CONTAINER_NAME_BET")
blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(BLOB_CONTAINER_NAME)

# Function to create or update Azure betting reference Blob Storage
def create_or_update_betting_reference_blob_storage(src_directory):
    for filename in os.listdir(src_directory):
        file_path = os.path.join(src_directory, filename)
        blob_client = container_client.get_blob_client(filename)
        # Only upload if the blob does not already exist
        if not blob_client.exists():
            with open(file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=False)
            print(f"Uploaded '{filename}' from directory '{src_directory}' to blob storage container '{BLOB_CONTAINER_NAME}'.")
        else:
            print(f"Skipped '{filename}': already exists in blob storage.")
    print("Betting reference blob storage has been created or updated.")

# Define main if running as standalone script
def main():
    create_or_update_betting_reference_blob_storage(REPO_LOCAL)

# Execute main if running as standalone script
if __name__ == "__main__":
    main()
