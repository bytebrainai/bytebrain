import json
import requests


def zio_ecosystem_projects():
    file_path = "index/zio-ecosystem.json"
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")


def get_zio_ecosystem_repo_info():
    base_url = f"https://api.github.com/orgs/zio/repos"
    headers = {"Accept": "application/vnd.github.v3+json"}  # Set headers to use GitHub API v3

    repo_infos = []
    page = 1
    per_page = 100  # Number of repositories per page

    while True:
        params = {"page": page, "per_page": per_page}
        response = requests.get(base_url, headers=headers, params=params)

        if response.status_code == 200:
            repos = response.json()
            if len(repos) == 0:
                break  # No more repositories to retrieve

            for repo in repos:
                clone_url = repo["clone_url"]
                default_branch = repo["default_branch"]
                print(clone_url)
                repo_infos.append({  # TODO: Add id field for each entry
                    "clone_url": clone_url,
                    "default_branch": default_branch
                })

            page += 1
        else:
            print(f"Failed to retrieve repositories. Error: {response.status_code} - {response.text}")
            return []

    with open("zio-ecosystem.json", 'w') as file:
        json.dump(repo_infos, file)
