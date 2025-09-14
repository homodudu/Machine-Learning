import os
import re
import pandas as pd
from dotenv import load_dotenv
from github import Github
from azure.storage.blob import BlobServiceClient

# Load environment variables from .env file
load_dotenv()
REPO_ATP = os.getenv("GITHUB_ATP_REPO")
REPO_WTA = os.getenv("GITHUB_WTA_REPO")
FILTER_START_YEAR = int(os.getenv("GITHUB_FILTER_START_YEAR"))
REPO_LOCAL = os.getenv("LOCAL_REPO_STATS")

# Set pandas options for better display
pd.set_option('display.max_colwidth', None)

# Initialize the GitHub client
github_token = os.getenv("GITHUB_ACCESS_TOKEN")
github_client = Github(github_token)

# Initialise the azure blob service container client
BLOB_CONNECTION_STRING = os.getenv("AZURE_BLOB_CONNECTION_STRING")
BLOB_CONTAINER_NAME = os.getenv("AZURE_BLOB_CONTAINER_NAME_STAT")
blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(BLOB_CONTAINER_NAME)

# Function to extract and filter CSV URLs from a GitHub repository
def _extract_and_filter_csv_urls_from_github_repo(repo_name, retrieval_start_year=FILTER_START_YEAR):
    repo = github_client.get_repo(repo_name)
    urls = [c.html_url for c in repo.get_contents("") if c.html_url.endswith('.csv')]
    urls = [l.replace("github", "raw.githubusercontent").replace("blob/", "refs/heads/") for l in urls]
    urls = [l for l in urls if re.search(r"\d{4}.csv", l)]
    urls = [l for l in urls if int(re.sub(r"\D", "", l)) >= retrieval_start_year]
    return urls

# Function to update the local repository with new Github URLs
def _update_url_archive_in_local_repo(urls, url_download_path):
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

# Function to download and update new URL content in the local repository
def _download_and_update_url_content_in_local_repo(new_urls, stat_download_path):
    df_master = pd.DataFrame()
    for url in new_urls:
        df_temp = pd.read_csv(url, sep=',', low_memory=False)
        df_master = pd.concat([df_master, df_temp], ignore_index=True)

    # If the master DataFrame is not empty, append it to the local stats file
    if not df_master.empty:
        df_master.to_csv(stat_download_path, sep=',', encoding='utf_8_sig', mode='a', header=True, index=False)
    return df_master

# Function to download GitHub tennis data to local repository and check for updates
def _download_github_tennis_data_to_local_repo(repo_name, retrieval_start_year=FILTER_START_YEAR):
    tour_type = repo_name[-3:].lower()
    url_local_repo_path = f"{REPO_LOCAL}/{tour_type}_url_data.csv"
    stat_local_repo_path = f"{REPO_LOCAL}/{tour_type}_stat_data.csv"

    filtered_urls = _extract_and_filter_csv_urls_from_github_repo(repo_name, retrieval_start_year)
    new_urls, initial = _update_url_archive_in_local_repo(filtered_urls,  url_local_repo_path)

    # If there are no new URLs and it's not the initial run, do not update the local repository
    if not initial and new_urls.empty:
        print(f"No new URLs found containing '{tour_type}' data, local repo will not be updated.")
        return False

    # If it is the initial run, ensure the stats file exists
    if initial and not os.path.exists(stat_local_repo_path):
        pd.DataFrame().to_csv(stat_local_repo_path, sep=',', encoding='utf_8_sig', index=False)

    # If there are new URLs, download and print the content
    if not new_urls.empty:
        df_master = _download_and_update_url_content_in_local_repo(new_urls, stat_local_repo_path)
        print(df_master)
        print(f"Updated local data archive with {repo_name} data.")
        return True

    # If initial run but no new URLs, still return True (repo initialized)
    if initial:
        print(f"Initialized local repo for '{tour_type}' data.")
        return True

    # Default: no update
    return False

# Function to upload local repository data to Azure Blob Storage and overwrite existing data
def _upload_local_repo_tennis_data_to_azure_blob_storage(src_directory, repo_name):
    tour_type = repo_name[-3:].lower()
    for filename in os.listdir(src_directory):
        if filename == (f"{tour_type}_stat_data.csv"):
            file_path = os.path.join(src_directory, filename)
            blob_client = container_client.get_blob_client(filename)
            with open(file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
            print(f"Uploaded '{filename}' from directory '{src_directory}' to blob storage.\n")

# Main function to update Azure blob storage with Github tennis stat data - to be equipped as an agentic tool.
def update_tennis_stats_blob_storage_resource(*repos):
    repo_set = set(repos)
    for repo in repo_set:
        local_repo_updated = _download_github_tennis_data_to_local_repo(repo)
        if local_repo_updated:
            _upload_local_repo_tennis_data_to_azure_blob_storage(REPO_LOCAL, repo)

# Define main if running as standalone script
def main():
    update_tennis_stats_blob_storage_resource(REPO_ATP, REPO_WTA)

# Execute main if running as standalone script
if __name__ == "__main__":
    main()
