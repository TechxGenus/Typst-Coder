import re
import sys
import json
import time
import requests

def get_repo_license(repo_url):
    pattern = r'https://github\.com/([^/]+)/([^/]+)'
    match = re.match(pattern, repo_url)

    if not match:
        return {"repo_url": repo_url, "license": ""}

    owner, repo = match.groups()
    api_url = f"https://api.github.com/repos/{owner}/{repo}/license"

    if len(sys.argv) > 1:
        headers = {"Authorization": f"Bearer {sys.argv[1]}"}
    else:
        headers = {}

    try:
        response = requests.get(api_url, headers=headers)
        
        while response.status_code != 200:
            if response.status_code == 403:
                print(f"Failed to query for repo: {repo_url}")
                print(response.json())
                time.sleep(10)
                response = requests.get(api_url, headers=headers)
            else:
                break
    except:
        return {"repo_url": repo_url, "license": ""}

    if response.status_code == 200:
        data = response.json()
        license_info = data.get("license", {}).get("name", "")
        return {"repo_url": repo_url, "license": license_info}
    else:
        return {"repo_url": repo_url, "license": ""}

def process_repos(input_json, output_json):
    with open(input_json, 'r') as f:
        repo_list = json.load(f)
    
    license_data = []
    total_repos = len(repo_list)
    print(f"Total repositories to process: {total_repos}.")
    
    import concurrent.futures

    def process_repo(repo_url):
        license_info = get_repo_license(repo_url)
        return repo_url, license_info

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_repo = {executor.submit(process_repo, repo_url): repo_url for repo_url in repo_list}
        
        for i, future in enumerate(concurrent.futures.as_completed(future_to_repo)):
            repo_url = future_to_repo[future]
            try:
                repo_url, license_info = future.result()
                license_data.append(license_info)

                print(f"Processing {i + 1}/{total_repos}: {repo_url}")
                print(f"Current License information: {license_info['license']}")
            except Exception as exc:
                print(f"An error occurred while processing {repo_url}: {exc}")

    with open(output_json, 'w') as f:
        json.dump(license_data, f, indent=4)
    
    print(f"All repositories processed, results saved to {output_json}")

input_json = "repos.json"
output_json = "licenses.json"
process_repos(input_json, output_json)
