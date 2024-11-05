import sys
import time
import json
import requests
from datetime import datetime, timedelta

url = "https://api.github.com/search/repositories"
if len(sys.argv) > 1:
    headers = {"Authorization": f"Bearer {sys.argv[1]}"}
else:
    headers = {}

start_date = datetime(2019, 9, 24) # 2019-09-24 is the first day of the Typst project on GitHub
end_date = datetime(2024, 10, 24)
current_date = start_date

repo_urls = []

while current_date <= end_date:
    date_str = current_date.strftime("%Y-%m-%d")

    for query in [f"language:Typst created:{date_str}", f"typst created:{date_str}"]:
        params = {
            "q": query,
            "sort": "created",
            "order": "desc",
            "per_page": 100,
            "page": 1
        }

        while True:
            response = requests.get(url, headers=headers, params=params)
            
            while response.status_code != 200:
                print(f"Failed to query for date: {date_str}")
                print(response.json())
                time.sleep(10)
                response = requests.get(url, headers=headers, params=params)
            
            data = response.json()

            if "items" not in data or len(data["items"]) == 0:
                break

            for repo in data["items"]:
                repo_urls.append(repo["html_url"])

            if "next" not in response.links:
                break

            params["page"] += 1

    print(f"Finished querying for date: {date_str}")
    current_date += timedelta(days=1)

repo_urls = list(set(repo_urls))
print(f"The number of repositories: {len(repo_urls)}")

with open("repos.json", "w") as f:
    json.dump(repo_urls, f, indent=4)
