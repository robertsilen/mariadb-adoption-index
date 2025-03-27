# How to get reddit oath access token
# Start by creating app in https://www.reddit.com/prefs/apps and enter values below: 

import requests

CLIENT_ID = ""
CLIENT_SECRET = ""
USERNAME = ""
PASSWORD = ""
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
print("Access Token:", TOKEN)
