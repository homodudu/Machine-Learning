import os
import requests
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.indexes.models import (
    SoftDeleteColumnDeletionDetectionPolicy,
    SearchIndexerDataSourceConnection,
    SearchIndexerDataContainer,
    SearchIndexerDataSourceType as DataSourceType
)

# Load environment variables from .env file
load_dotenv()

# Azure Open AI settings
OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

# Azure Blob Storage settings
BLOB_CONNECTION_STRING = os.getenv("AZURE_BLOB_CONNECTION_STRING")
BLOB_CONTAINER_NAME = os.getenv("AZURE_BLOB_CONTAINER_NAME")
BLOB_DATA_SOURCE_NAME = os.getenv("AZURE_BLOB_DATA_SOURCE_NAME")

# Azure AI Search settings
SEARCH_ENDPOINT = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
SEARCH_API_KEY = os.getenv("AZURE_AI_SEARCH_API_KEY")
SEARCH_INDEX_NAME = os.getenv("AZURE_AI_SEARCH_INDEX")
SEARCH_INDEX_PATH = os.getenv("AZURE_AI_SEARCH_INDEX_CONFIG_PATH")
SEARCH_INDEXER_NAME =  os.getenv("AZURE_AI_SEARCH_INDEXER")
SEARCH_INDEXER_PATH = os.getenv("AZURE_AI_SEARCH_INDEXER_CONFIG_PATH")
SEARCH_SKILLSET_NAME =  os.getenv("AZURE_AI_SEARCH_SKILLSET")
SEARCH_SKILLSET_PATH = os.getenv("AZURE_AI_SEARCH_SKILLSET_CONFIG_PATH")
SEARCH_VECTORIZER_NAME = os.getenv("AZURE_AI_SEARCH_VECTORIZER")

# Initialize Azure Search Indexer Client
index_client = SearchIndexClient(endpoint=SEARCH_ENDPOINT, credential=AzureKeyCredential(SEARCH_API_KEY))
# index_client.delete_index(SEARCH_INDEX_NAME)

# Initialize Azure Search Indexer Client
indexer_client = SearchIndexerClient(endpoint=SEARCH_ENDPOINT, credential=AzureKeyCredential(SEARCH_API_KEY))

# Function to create or update the data source connection
def _create_or_update_datasource_connection(data_source_name, container_name, connection_string):
    # Create the data source connection for Azure Blob Storage
    data_source_connection = SearchIndexerDataSourceConnection(
        name=data_source_name,
        type=DataSourceType.AZURE_BLOB,
        container=SearchIndexerDataContainer(name=container_name),
        connection_string=connection_string,
        data_deletion_detection_policy=SoftDeleteColumnDeletionDetectionPolicy(
            soft_delete_column_name="IsDeleted",
            soft_delete_marker_value="True"
        )
    )
    indexer_client.create_or_update_data_source_connection(data_source_connection)
    print(f"Data source '{data_source_name}' connection created or updated.\n")

# Function to deploy azure search JSON configuration via API call
def _deploy_json_config_via_api_call(filepath, url, api_key):
    headers = {"Content-Type": "application/json", "api-key": api_key}
    with open(filepath) as f:
        index_json = f.read()
    try:
        response = requests.put(url, headers=headers, data=index_json)
        response.raise_for_status()
        print(f"JSON configuration from '{filepath}' has succesfully deployed to Azure search (status code: {response.status_code} ")
    except requests.exceptions.HTTPError as e:
        raise Exception(f"JSON configuration from '{filepath}' has failed deployment to Azure search (status code: {response.status_code})")

# Function to create or update the search index
def _create_or_update_search_index(index_name, filepath,  api_endpoint, api_key):
    _deploy_json_config_via_api_call(filepath,f"{api_endpoint}indexes/{index_name}?api-version={OPENAI_API_VERSION}", api_key)
    print(f"Index '{index_name}' created or updated via JSON.\n")

# Function to create or update the search indexer
def _create_or_update_search_indexer(indexer_name, filepath,  api_endpoint, api_key):
    _deploy_json_config_via_api_call(filepath, f"{api_endpoint}indexers/{indexer_name}?api-version={OPENAI_API_VERSION}", api_key)
    print(f"Indexer '{indexer_name}' created or updated via JSON.\n")

# Function to create or update the search indexer skillset
def _create_or_update_indexer_skillset(skillset_name, filepath,  api_endpoint, api_key):
    _deploy_json_config_via_api_call(filepath,f"{api_endpoint}skillsets/{skillset_name}?api-version={OPENAI_API_VERSION}", api_key)
    print(f"Skillset '{skillset_name}' skillset created or updated via JSON.\n")

# Main function to create or update Azure Cognitive Search components - to be equipped as agentic tool
def create_or_update_azure_search(
        blob_data_source_name,
        blob_container_name,
        blob_connection_string,
        search_index_name,
        search_index_path,
        search_indexer_name,
        search_indexer_path,
        search_endpoint,
        search_api_key,
        search_skillset_name,
        search_skillset_path
        ):

    _create_or_update_datasource_connection(blob_data_source_name, blob_container_name, blob_connection_string)
    _create_or_update_search_index(search_index_name, search_index_path, search_endpoint, search_api_key)
    _create_or_update_search_indexer(search_indexer_name, search_indexer_path, search_endpoint, search_api_key)
    _create_or_update_indexer_skillset(search_skillset_name, search_skillset_path, search_endpoint, search_api_key)

    # Run the indexer to load data from blob into the index
    indexer_client.run_indexer(search_indexer_name)
    print(f"Indexer '{search_indexer_name}' has ran sucessfully. New data will be indexed into '{search_index_name}' if it exists.\n")

if __name__ == "__main__":
    create_or_update_azure_search(
        BLOB_DATA_SOURCE_NAME,
        BLOB_CONTAINER_NAME,
        BLOB_CONNECTION_STRING,
        SEARCH_INDEX_NAME,
        SEARCH_INDEX_PATH,
        SEARCH_INDEXER_NAME,
        SEARCH_INDEXER_PATH,
        SEARCH_ENDPOINT,
        SEARCH_API_KEY,
        SEARCH_SKILLSET_NAME,
        SEARCH_SKILLSET_PATH
    )
