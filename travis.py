import os
import requests
import time
from pprint import pprint

from dotenv import load_dotenv

load_dotenv()
GITHUB_ACCESS_TOKEN = os.getenv('GITHUB_ACCESS_TOKEN')
GITHUB_SEARCH_API = os.getenv('GITHUB_SEARCH_API')
TRAVIS_ISSUES_PARAMS = os.getenv('TRAVIS_ISSUES_PARAMS')
TRAVIS_FILE_PARAMS = os.getenv('TRAVIS_FILE_PARAMS')
GITHUB_REPO_URL = os.getenv('GITHUB_REPO_URL')
PROJECT_PATH = os.getenv('PROJECT_PATH')

OUTPUT_FILE_PATH = f"{PROJECT_PATH}/repositories.csv"

def send_request(url, gh_token, ignore_token=False, sleep_time=1):
  headers = {}
  if not ignore_token:
    headers = {'Authorization': 'token %s' % gh_token}
  res = requests.get(url, headers=headers)
  time.sleep(sleep_time)
  response = res.json()
  return response

def get_repository_name(travis_issues):
  repositories = list()
  for issue in travis_issues["items"]:
    try:
      repository_name = issue["repository_url"].split('/repos/')[1]
      files_in_repository = send_request(GITHUB_SEARCH_API+TRAVIS_FILE_PARAMS+repository_name, GITHUB_ACCESS_TOKEN)
      if files_in_repository["total_count"] > 0:
          files_searched = files_in_repository["items"]
          for file in files_searched:
              if file["name"] == '.travis.yml':
                repositories.append(repository_name)
    except Exception as e:
      print(f"ERROR: Failed getting .travis.yml file for repo={repository_name}")
  return(repositories)

def create_csv_file_if_necessary(file_path, headers):
    if not os.path.isfile(file_path):
        with open(file_path, 'w') as csv_file:
            writer = csv.DictWriter(csv_file, headers)
            writer.writeheader()

def main():
  repository_data = list()
  if GITHUB_ACCESS_TOKEN is None:
    raise Exception("No GITHUB_ACCESS_TOKEN")
  travis_issues = send_request(GITHUB_SEARCH_API+TRAVIS_ISSUES_PARAMS, GITHUB_ACCESS_TOKEN)
  repo_names = get_repository_name(travis_issues)
  for repo in repo_names:
    repository_data.append(send_request(GITHUB_REPO_URL+repo, GITHUB_ACCESS_TOKEN))
  pprint(repository_data)
  create_csv_file_if_necessary(OUTPUT_FILE_PATH, OUTPUT_FILE_FIELD_NAMES)

if __name__ == "__main__":
    main()
