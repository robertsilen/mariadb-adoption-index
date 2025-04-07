# How to get reddit oath access token
# Start by creating app in https://www.reddit.com/prefs/apps and enter values below: 

import requests
import os

# Get credentials from environment variables
CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USERNAME = os.getenv("REDDIT_USERNAME")
PASSWORD = os.getenv("REDDIT_PASSWORD")
USER_AGENT = "mariadb script/0.1 by mariadb"

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

TOKEN = response.json().get("access_token")
# Save token to environment variable
os.environ["REDDIT_TOKEN"] = TOKEN
