import re
import sys
import json
import time
import requests
import concurrent.futures

def get_files_from_repo(repo_url, headers):
    repo_pattern = r'https://github\.com/([^/]+)/([^/]+)'
    repo_match = re.match(repo_pattern, repo_url)
    
    if not repo_match:
        return {"repo_url": repo_url, "files": []}
    
    owner, repo = repo_match.groups()
    
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
    
    def fetch_repo_contents(api_url):
        try:
            response = requests.get(api_url, headers=headers)
            while response.status_code != 200:
                if response.status_code == 403:
                    print(f"Failed to query for repo: {repo_url}")
                    print(response.json())
                    time.sleep(600)
                    response = requests.get(api_url, headers=headers)
                else:
                    break
        except:
            print(f"Failed to query for repo: {repo_url}")
            return []
        if response.status_code == 200:
            repo_contents = response.json()
            file_contents = []
            for item in repo_contents:
                if item['type'] == 'dir':
                    file_contents.extend(fetch_repo_contents(item['url']))
                elif item['type'] == 'file' and (item['name'].endswith(".typ") or item['name'].endswith(".md")):
                    file_content = fetch_file_content(item['download_url'])
                    if file_content:
                        file_contents.append({"content": file_content, "file": item['download_url'], "language": "typst" if item['name'].endswith(".typ") else "markdown"})
            return file_contents
        else:
            print(f"Error fetching contents: {response.status_code}")
            return []

    def fetch_file_content(file_url):
        try:
            response = requests.get(file_url, headers=headers)
            while response.status_code != 200:
                if response.status_code == 403:
                    print(f"Failed to query for file: {file_url}")
                    print(response.json())
                    time.sleep(600)
                    response = requests.get(file_url, headers=headers)
                else:
                    break
        except:
            return None
        if response.status_code == 200:
            return response.text
        else:
            print(f"Error fetching file content: {response.status_code}")
            return None

    files = fetch_repo_contents(api_url)
    
    return files

def process_repos(input_json_path, output_json_path):
    with open(input_json_path, 'r') as input_file:
        repo_list = json.load(input_file)
    
    all_files_data = []
    total_repos = len(repo_list)
    
    print(f"Total {total_repos} repos to process.")
    
    if len(sys.argv) > 1:
        headers = {"Authorization": f"Bearer {sys.argv[1]}"}
    else:
        headers = {}
    
    def process_single_repo(repo_info):
        repo_files = get_files_from_repo(repo_info["repo_url"], headers)
        repo_files = [{"content": file_info["content"], "file": file_info["file"], "language": file_info["language"], "repo": repo_info["repo_url"], "license": repo_info["license"]} for file_info in repo_files]
        return repo_files

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_repo = {executor.submit(process_single_repo, repo_info): repo_info["repo_url"] for repo_info in repo_list}
        
        for i, future in enumerate(concurrent.futures.as_completed(future_to_repo)):
            repo_url = future_to_repo[future]
            try:
                repo_files = future.result()
                all_files_data.extend(repo_files)
                
                print(f"Processing {i + 1}/{total_repos}: {repo_url}")
                print(f"File count: {len(repo_files)}")
            except Exception as exc:
                print(f"{repo_url} processing error: {exc}")
        
    with open(output_json_path, 'w') as output_file:
        json.dump(all_files_data, output_file, indent=4)
    
    print(f"All repos processed, results saved to {output_json_path}")

input_json_path = "licenses.json"
output_json_path = "files.json"
process_repos(input_json_path, output_json_path)
