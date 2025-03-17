import requests

access_token='p1wBavbMsbdL-pt0KUFpuU_97XGYcFs7wMpa9o0e0zA',  # Replace with your Mastodon app access token

# Fetch user ID for the account
user_name = 'mariadb'
url = f'https://fosstodon.org/api/v1/accounts/lookup?username={user_name}'

headers = {
    'Authorization': f'Bearer {access_token}'
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    user_data = response.json()
    user_id = user_data['id']
    print(f'User ID for {user_name}: {user_id}')

    # Now, fetch the followers using the user ID
    followers_url = f'https://fosstodon.org/api/v1/accounts/{user_id}/followers'
    followers_response = requests.get(followers_url, headers=headers)

    if followers_response.status_code == 200:
        followers = followers_response.json()
        print(f'Followers of {user_name}:')
        for follower in followers:
            print(follower['username'])
    else:
        print('Failed to fetch followers')
else:
    print('Failed to fetch user data')
