import os
import re
import pandas as pd
from dotenv import load_dotenv
from github import Github
from datetime import datetime
from azure.storage.blob import BlobServiceClient

# Load environment variables from .env file
load_dotenv()

class HandlerGithubStats:
    """
    Class that handles the download and storage of tennis statistcs from public Github repositories.\n

    github_client: The Github client that has been instantiated.\n
    repo_local: The directory path of the local Github repository.\n
    list_repo_urls: The list of Github repository urls to download data from.\n
    blob_connection_string: The blob connection string.\n
    blob_container_name: The blob contaainer name.\n
    """
    def __init__(self, github_client, repo_local, list_repo_urls, blob_connection_string, blob_container_name):
        self.github_client = github_client
        self.repo_local = repo_local
        self.list_repo_urls = list_repo_urls
        self.blob_service_client = BlobServiceClient.from_connection_string(blob_connection_string)
        self.container_client = self.blob_service_client.get_container_client(blob_container_name)

    def _extract_and_filter_csv_urls_from_github_repo(self, repo_name, filter_start_year):
        if filter_start_year == None:
            filter_start_year = int(datetime.now().year) - 1
        repo = self.github_client.get_repo(repo_name)
        urls = [c.html_url for c in repo.get_contents("") if c.html_url.endswith('.csv')]
        urls = [l.replace("github", "raw.githubusercontent").replace("blob/", "refs/heads/") for l in urls]
        urls = [l for l in urls if re.search(r"\d{4}.csv", l)]
        urls = [l for l in urls if int(re.sub(r"\D", "", l)) >= filter_start_year]
        return urls

    def _update_url_archive_in_local_repo(self, urls, url_download_path):
        df_urls = pd.DataFrame({"URL": urls})
        initial = not os.path.exists(url_download_path)

        # If the file does not exist, create it and write the URLs
        if initial:
            df_urls.to_csv(url_download_path, sep='\t', encoding='utf_8_sig', index=False)
            return df_urls["URL"], initial

        # If the file exists, read it and append new URLs
        df_url_archive = pd.read_csv(url_download_path, sep=',', index_col=False)
        new_urls = df_urls[~df_urls["URL"].isin(df_url_archive["URL"])]["URL"]
        if not new_urls.empty:
            new_urls.to_csv(url_download_path, sep=',', mode='a', encoding='utf_8_sig', header=False, index=False)
        return new_urls, initial

    def _download_and_update_url_content_in_local_repo(self, new_urls, stat_download_path):
        df_master = pd.DataFrame()
        for url in new_urls:
            df_temp = pd.read_csv(url, sep=',', low_memory=False)
            df_master = pd.concat([df_master, df_temp], ignore_index=True)

        # If the master DataFrame is not empty, append it to the local stats file
        if not df_master.empty:
            df_master.to_csv(stat_download_path, sep=',', encoding='utf_8_sig', mode='a', header=True, index=False)
        return df_master

    def download_github_tennis_data(self, filter_start_year):
        repo_data_dict = {} # # Dictionary to store entire URL content {tour_type: DataFrame}
        # Iterate through each github repo and download tennis data
        for repo_name in self.list_repo_urls:
            tour_type = repo_name[-3:].lower()
            url_local_repo_path = f"{self.repo_local}/{tour_type}_url_data.csv"
            stat_local_repo_path = f"{self.repo_local}/{tour_type}_stat_data.csv"

            filtered_urls = self._extract_and_filter_csv_urls_from_github_repo(repo_name, filter_start_year)
            new_urls, initial = self._update_url_archive_in_local_repo(filtered_urls,  url_local_repo_path)

            # If there are no new URLs and it's not the initial run, do not update the local repository
            if not initial and new_urls.empty:
                print(f"No new URLs found containing '{tour_type}' data, local repo will not be updated.")
                # Add an empty DataFrame for this tour_type
                repo_data_dict[tour_type] = pd.DataFrame()
                # Continue to next loop iteration
                continue

            # If it is the initial run, ensure the stats file exists
            if initial and not os.path.exists(stat_local_repo_path):
                pd.DataFrame().to_csv(stat_local_repo_path, sep=',', encoding='utf_8_sig', index=False)

            # If there are new URLs, download and print the content
            if not new_urls.empty:
                df_master = self._download_and_update_url_content_in_local_repo(new_urls, stat_local_repo_path)
                repo_data_dict[tour_type] = df_master # Store url content in dictionary with tour type as key
                print(df_master)
                print(f"Updated local data archive with {repo_name} data.")

            # If initial run but no new URLs, still return True (repo initialized)
            if initial:
                print(f"Initialized local repo with '{tour_type}' data.")

        return repo_data_dict

    def upload_data_to_blob_storage(self, repo_data_dict):
        for tour_type, data in repo_data_dict.items():
            if data.empty:
                print(f"No new '{tour_type}' data found. Blob storage container '{self.container_client.container_name}' will not be updated.")
                continue
            filename = f"{tour_type}_stat_data.csv"
            blob_client = self.container_client.get_blob_client(filename)
            blob_client.upload_blob(data.to_csv(index=False), overwrite=True)
            print(f"Updated blob storage container '{self.container_client.container_name}' with '{tour_type}'. Uploaded '{filename}'.")

# Usage example (can be called by a azure foundry agent tool)
def main():
    REPO_ATP = os.getenv("GITHUB_ATP_REPO")
    REPO_WTA = os.getenv("GITHUB_WTA_REPO")
    FILTER_START_YEAR = int(os.getenv("GITHUB_FILTER_START_YEAR"))
    REPO_LOCAL = os.getenv("LOCAL_REPO_STATS")

    # Set pandas options for better display
    pd.set_option('display.max_colwidth', None)

    # Initialize the GitHub client
    GITHUB_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")
    github_client = Github(GITHUB_TOKEN)

    # Initialise the azure blob service container client
    BLOB_CONNECTION_STRING = os.getenv("AZURE_BLOB_CONNECTION_STRING")
    BLOB_CONTAINER_NAME = os.getenv("AZURE_BLOB_CONTAINER_NAME_STAT")

    handler_git_hub_stats = HandlerGithubStats(github_client, REPO_LOCAL, [REPO_ATP, REPO_WTA], BLOB_CONNECTION_STRING, BLOB_CONTAINER_NAME)
    tennis_blob_data = handler_git_hub_stats.download_github_tennis_data(FILTER_START_YEAR)
    handler_git_hub_stats.upload_data_to_blob_storage(tennis_blob_data)

# Execute main if running as standalone script
if __name__ == "__main__":
    main()
