import requests
import csv
from datetime import datetime
import os  # Add this import to access environment variables

# GitHub API URL for the repository's pull requests
url = "https://api.github.com/repos/mariadb/server/pulls"
params = {
    "state": "all",
    "sort": "created",
    "direction": "desc",
    "per_page": 100,
}


token = os.getenv('GH_TOKEN')  
if token is None: 
    print("Warning: GH_TOKEN is not set. Please set it in your environment variables.")
headers = {
    "Authorization": f"token {token}" 
}

# Prepare to collect PR data
pr_data = []
done = False

# Iterate through up to 10 pages
for page in range(1, 100):
    params['page'] = page
    response = requests.get(url, params=params, headers=headers)  # Include headers in the request
    
    if response.status_code == 200:
        prs = response.json()
        if not prs:  # Stop if no more PRs are returned
            break
        
        oldest_date = None  # Initialize oldest date for the current page
        for pr in prs:
            created_date = pr["created_at"]
            # Check if the created date is older than 2023-01-01
            if datetime.strptime(created_date, "%Y-%m-%dT%H:%M:%SZ") < datetime(2023, 1, 1):
                done = True
                break
            
            # Update oldest date if it's the first PR or older than the current oldest
            if oldest_date is None or created_date < oldest_date:
                oldest_date = created_date

            labels = [label['name'] for label in pr['labels']]
            pr_info = {
                "PR-number": pr["number"],
                "labels": ', '.join(labels) if labels else '',
                "created_date": created_date,
                "creator_username": pr["user"]["login"],
                'status': pr['state'],
                "PR-title": pr["title"],
                "PR-URL": pr["html_url"],
            }
            pr_data.append(pr_info)
        
        # Print the oldest date for the current page and total fetched
        print(f"Page {page}: Oldest PR date: {oldest_date}, Total fetched so far: {len(pr_data)}")
    else:
        print(f"Failed to fetch data: {response.status_code}")
        break
    if done:
        break

# Save results to a CSV file
if pr_data:  # Check if pr_data is not empty
    with open('data/github_new_prs_unique_contributors/since-2023-01-01.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=pr_data[0].keys())
        writer.writeheader()
        writer.writerows(pr_data)
else:
    print("No PR data to save.")

print("Data saved to data/github_new_prs_unique_contributors/since-2023-01-01.csv")