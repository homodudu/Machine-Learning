
import os
import requests
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import  SearchIndexClient, SearchIndexerClient
from azure.search.documents.indexes.models import (
    SoftDeleteColumnDeletionDetectionPolicy,
    SearchIndexerDataSourceConnection,
    SearchIndexerDataContainer,
    SearchIndexerDataSourceType as DataSourceType
)

# Load environment variables from .env file
load_dotenv()

# Azure Open AI settings
OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

# Create the Azure search handler class (to be instantiated for any agent)
class HandlerAgentSearch:
    """
    Class that handles the Azure AI Search resource for a user agent.\n

    blob_data_source_name: The blob data source name.\n
    blob_container_name: The blob container name.\n
    blob_connection_string: The blob connection string.\n
    search_index_name: The search index name.\n
    search_index_path: The path of the search index json config file.\n
    search_indexer_name: The search indexer name.\n
    search_indexer_path: The path of the search indexer json config file.\n
    search_endpoint: The azure search endpoint.\n
    search_api_key: The azure search api key.\n
    search_skillset_name: The search skillset name.\n
    search_skillset_path: The path of the search skillset json config file.\n
    """
    def __init__(self,
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
                 search_skillset_path):
        self._blob_data_source_name = blob_data_source_name
        self._blob_container_name = blob_container_name
        self._blob_connection_string = blob_connection_string
        self._search_index_name = search_index_name
        self._search_index_path = search_index_path
        self._search_indexer_name = search_indexer_name
        self._search_indexer_path = search_indexer_path
        self._search_endpoint = search_endpoint
        self._search_api_key = search_api_key
        self._search_skillset_name = search_skillset_name
        self._search_skillset_path = search_skillset_path

        self._index_client = SearchIndexClient(endpoint=search_endpoint, credential=AzureKeyCredential(search_api_key))
        self._indexer_client = SearchIndexerClient(endpoint=search_endpoint, credential=AzureKeyCredential(search_api_key))

    def _delete_all_documents_from_index(self):
        search_client = SearchClient(endpoint=self._search_endpoint, index_name=self._search_index_name, credential=AzureKeyCredential(self._search_api_key))
        results = search_client.search("*", select=["chunk_id"])
        ids = [doc["chunk_id"] for doc in results]
        if ids:
            search_client.delete_documents(documents=[{"chunk_id": id} for id in ids])
            print(f"Deleted {len(ids)} documents from index '{self._search_index_name}'\n.")
        else:
            print(f"No documents found to delete from index '{self._search_index_name}'\n.")

    def _create_or_update_datasource_connection(self):
        data_source_connection = SearchIndexerDataSourceConnection(
            name=self._blob_data_source_name,
            type=DataSourceType.AZURE_BLOB,
            container=SearchIndexerDataContainer(name=self._blob_container_name),
            connection_string=self._blob_connection_string,
            data_deletion_detection_policy=SoftDeleteColumnDeletionDetectionPolicy(
                soft_delete_column_name="IsDeleted",
                soft_delete_marker_value="True"
            )
        )
        self._indexer_client.create_or_update_data_source_connection(data_source_connection)
        print(f"Data source '{self._blob_data_source_name}' connection created or updated.\n")

    def _deploy_json_config_via_api_call(self, filepath, url):
        headers = {"Content-Type": "application/json", "api-key": self._search_api_key}
        with open(filepath) as f:
            index_json = f.read()
        response = requests.put(url, headers=headers, data=index_json)
        response.raise_for_status()
        print(f"JSON configuration from '{filepath}' has successfully deployed to Azure search (status code: {response.status_code})")

    def _create_or_update_search_index(self):
        self._delete_all_documents_from_index()
        self._deploy_json_config_via_api_call(
            self._search_index_path,
            f"{self._search_endpoint}indexes/{self._search_index_name}?api-version={OPENAI_API_VERSION}"
        )
        print(f"Index '{self._search_index_name}' created or updated via JSON.\n")

    def _create_or_update_search_indexer(self):
        self._deploy_json_config_via_api_call(
            self._search_indexer_path,
            f"{self._search_endpoint}indexers/{self._search_indexer_name}?api-version={OPENAI_API_VERSION}"
        )
        print(f"Indexer '{self._search_indexer_name}' created or updated via JSON.\n")

    def _create_or_update_indexer_skillset(self):
        self._deploy_json_config_via_api_call(
            self._search_skillset_path,
            f"{self._search_endpoint}skillsets/{self._search_skillset_name}?api-version={OPENAI_API_VERSION}"
        )
        print(f"Skillset '{self._search_skillset_name}' skillset created or updated via JSON.\n")

    def create_or_update_azure_search_with_blob_data(self):
        self._create_or_update_datasource_connection()
        self._create_or_update_search_index()
        self._create_or_update_search_indexer()
        self._create_or_update_indexer_skillset()
        self._indexer_client.run_indexer(self._search_indexer_name)
        print(f"Indexer '{self._search_indexer_name}' has run successfully. New data will be indexed into '{self._search_index_name}' if it exists.\n")

# Usage example (can be called by a azure foundry agent tool)
def main():
    # Azure Blob Storage settings for creating or updating statistics agent
    BLOB_CONNECTION_STRING = os.getenv("AZURE_BLOB_CONNECTION_STRING")
    BLOB_CONTAINER_NAME = os.getenv("AZURE_BLOB_CONTAINER_NAME_STAT")
    BLOB_DATA_SOURCE_NAME = os.getenv("AZURE_BLOB_DATA_SOURCE_NAME_STAT")

    # Azure AI Search settings for creating or updating statistics agent
    SEARCH_ENDPOINT = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
    SEARCH_API_KEY = os.getenv("AZURE_AI_SEARCH_API_KEY")
    SEARCH_INDEX_NAME = os.getenv("AZURE_AI_SEARCH_INDEX_STAT")
    SEARCH_INDEX_PATH = os.getenv("AZURE_AI_SEARCH_INDEX_CONFIG_PATH_STAT")
    SEARCH_INDEXER_NAME =  os.getenv("AZURE_AI_SEARCH_INDEXER_STAT")
    SEARCH_INDEXER_PATH = os.getenv("AZURE_AI_SEARCH_INDEXER_CONFIG_PATH_STAT")
    SEARCH_SKILLSET_NAME =  os.getenv("AZURE_AI_SEARCH_SKILLSET_STAT")
    SEARCH_SKILLSET_PATH = os.getenv("AZURE_AI_SEARCH_SKILLSET_CONFIG_PATH_STAT")

    # Create agent search handler example for statistics agent
    handler_stats_agent_search = HandlerAgentSearch(
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
    # Run and update the Azure AI search resource used by the statistics agent
    handler_stats_agent_search.create_or_update_azure_search_with_blob_data()

if __name__ == "__main__":
    main()
