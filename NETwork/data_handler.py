import os
import ssl
import re
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
from github import Github

# Load environment variables from .env file
load_dotenv()

# Set pandas options for better display
pd.set_option('display.max_colwidth', None)

# Get most recent year to use as data retrieval parameter
MOST_RECENT_YEAR = datetime.now().year - 1


def retrieve_github_tennis_stats(repo_name, retrieval_start_year=MOST_RECENT_YEAR):
    """
    Retrieves the latest tennis statistics from a GitHub repository.
    It retrieves URLs of CSV files, checks for updates, and appends new data to local archives.
    """
    #  Extract the tennis "tour" type (WTA, ATP) from the GitHub repository name
    tour_type = repo_name[-3:].lower()

    # Define constants for file paths and retrieval settings
    URL_ARCHIVE_PATH = f"./NETwork/{tour_type}_url_data.csv"
    STAT_ARCHIVE_PATH = f"./NETwork/{tour_type}_stat_data.csv"
    COLUMN_URL = "URL"

    # Create an unverified SSL context to avoid certificate verification issues
    ssl._create_default_https_context = ssl._create_unverified_context

    # Authenticate GitHub client
    github_token = os.getenv("GITHUB_ACCESS_TOKEN")
    g = Github(github_token)

    # Get the repository
    repo = g.get_repo(repo_name)

    # Filter URLs from the repository contents
    list_of_urls = [c.html_url for c in repo.get_contents("")]
    list_of_urls = [l for l in list_of_urls if l.endswith('.csv')]

    # Replace Github url path with raw html path.
    list_of_urls = [l.replace("github", "raw.githubusercontent") for l in list_of_urls]
    list_of_urls = [l.replace("blob/", "refs/heads/") for l in list_of_urls]

    # Filter URLs to include only those with a year in the filename and ensure they are from 2024 or later
    list_of_urls = [l for l in list_of_urls if re.search(r"\d{4}.csv", l)]
    list_of_urls = [l for l in list_of_urls if int(re.sub(r"\D","",l)) >= retrieval_start_year]

    df_urls = pd.DataFrame({COLUMN_URL: list_of_urls})

    # Check if a URL archive file exists locally
    if not os.path.exists(URL_ARCHIVE_PATH):
        print(f"{tour_type}_stat_urls.csv does not exist locally. Creating the file.")
        df_urls.to_csv(URL_ARCHIVE_PATH, index=False)
        initial_url_retrieval = True
    else: initial_url_retrieval = False

   # Read the archived URL file into a dataframe
    df_url_archive =  pd.read_csv(URL_ARCHIVE_PATH, index_col=False)

    # Identify URLs that are unique to the repository based on the initial retrieval flag
    list_urls_unique_to_repo = ""
    if initial_url_retrieval is True:
        list_urls_unique_to_repo = df_urls[COLUMN_URL]
    else:
        list_urls_unique_to_repo = df_urls[~df_urls[COLUMN_URL].isin(df_url_archive[COLUMN_URL])]
        list_urls_unique_to_repo = list_urls_unique_to_repo[COLUMN_URL]

    # Check if repository has been updated with new URLs
    if df_urls.size == df_url_archive.size and initial_url_retrieval is False:
        print("No new URLs found. Local archive files will not be updated.")

    # Update the locally archived files if new URL's are found
    else:
        # Append new URLs to the URL archive file
        print("Updating URL archive.")
        if not list_urls_unique_to_repo.empty and initial_url_retrieval is False:
            list_urls_unique_to_repo.to_csv(URL_ARCHIVE_PATH, mode='a', header=False, index=False)
            print(f"{len(list_urls_unique_to_repo)} new URLs appended to URL archive:\n")
            print(f"{list_urls_unique_to_repo}\n")

        # Check if a data archive file exists locally
        if not os.path.exists(STAT_ARCHIVE_PATH):
            print(f"{tour_type}_stat_data.csv does not exist locally. Creating the file.")
            # Create new data archive file
            pd.DataFrame().to_csv(STAT_ARCHIVE_PATH, index=False)

        # Create master DataFrame
        df_master = pd.DataFrame()

        # Append new data to the DATA archive file
        if not list_urls_unique_to_repo.empty:
            print("Updating DATA archive.")
            for url in list_urls_unique_to_repo:
                df_temp = pd.read_csv(url, low_memory=False)
                df_master = pd.concat([df_master, df_temp], ignore_index=True)
            df_master.to_csv(STAT_ARCHIVE_PATH, mode='a', header=False, index=False)
            print("New data appended to data archive.")

# Main function to execute the script
def main():
    repo_atp = os.getenv("GITHUB_ATP_REPO")
    repo_wta = os.getenv("GITHUB_WTA_REPO")
    repo_list = {repo_atp, repo_wta}

    for repo in repo_list:
        retrieve_github_tennis_stats(repo)
        print(f"Data handler script executed successfully for repo: {repo}.")

# Entry point for the script
if __name__ == "__main__":
    main()
