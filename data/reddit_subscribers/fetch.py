# How to get reddit oath access token and fetch subscriber count
# Start by creating app in https://www.reddit.com/prefs/apps and enter values below: 

import requests
import os
import sys

# Get credentials from environment variables
CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USERNAME = os.getenv("REDDIT_USERNAME")
PASSWORD = os.getenv("REDDIT_PASSWORD")
USER_AGENT = "mariadb script/0.1 by mariadb"

def get_auth_token():
    # Request an access token
    auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    data = {
        "grant_type": "password",
        "username": USERNAME,
        "password": PASSWORD,
    }
    headers = {"User-Agent": USER_AGENT}

    response = requests.post(
        "https://www.reddit.com/api/v1/access_token",
        auth=auth,
        data=data,
        headers=headers,
    )

    return response.json().get("access_token")

def get_subscriber_count(token):
    headers = {
        "Authorization": f"bearer {token}",
        "User-Agent": USER_AGENT
    }
    
    response = requests.get(
        "https://oauth.reddit.com/r/mariadb/about.json",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"Error from Reddit API: {response.text}", file=sys.stderr)
        sys.exit(1)
        
    data = response.json()
    if 'error' in data:
        print(f"Error from Reddit API: {data}", file=sys.stderr)
        sys.exit(1)
        
    subscribers = data.get('data', {}).get('subscribers')
    if subscribers is None:
        print("Error: Failed to get valid subscriber count from Reddit API", file=sys.stderr)
        print(f"API Response: {data}", file=sys.stderr)
        sys.exit(1)
        
    return subscribers

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--subscribers":
        token = get_auth_token()
        subscribers = get_subscriber_count(token)
        print(subscribers)
    else:
        # Default behavior: just print the token
        token = get_auth_token()
        print(token)
