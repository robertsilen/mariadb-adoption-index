import requests

url = "https://api.github.com/search/repositories"
query = "mariadb in:readme"
params = {
    "q": query,
    "per_page": 100,  # Adjust as needed
    "page": 1
}

response = requests.get(url, params=params)
if response.status_code == 200:
    data = response.json()
    total_count = data['total_count']
    print(f"Total repositories with 'mariadb' in README: {total_count}")
else:
    print("Error fetching data from GitHub API:", response.status_code)
