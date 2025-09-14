# Load packages
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
blob_atp = os.getenv("AZURE_BLOB_ATP")
blob_wta = os.getenv("AZURE_BLOB_WTA")

# Azure Blob Storage settings
BLOB_CONNECTION_STRING = os.getenv("AZURE_BLOB_CONNECTION_STRING")
BLOB_CONTAINER_NAME = os.getenv("AZURE_BLOB_CONTAINER_NAME")
BLOB_DATA_SOURCE_NAME = os.getenv("AZURE_BLOB_DATA_SOURCE_NAME")

# download and print blob data
from azure.storage.blob import BlobServiceClient

blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(BLOB_CONTAINER_NAME)

print("Files in blob container:")
for blob in container_client.list_blobs():
    print(blob.name)

blob_name = "wta_stat_data_csv"
blob_client = container_client.get_blob_client(blob_name)
data = blob_client.download_blob().readall()

# If it's a text file
# print(data.decode("utf-8"))

print("Blob metadata in container:")
for blob in container_client.list_blobs():
    print(f"Name: {blob.name}")
    print(f"Last Modified: {blob.last_modified}")
    print(f"Content Type: {blob.content_settings.content_type}")
    print(f"Size: {blob.size}")
    print(f"Metadata: {blob.metadata}")
    print("-" * 40)
