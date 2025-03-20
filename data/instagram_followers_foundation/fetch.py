import instaloader
import csv
from datetime import datetime
import os

L = instaloader.Instaloader(download_pictures=False)
profile = instaloader.Profile.from_username(L.context, "mariadb_org")
print(profile.followers)

# Get today's date in YYYY-MM-DD format
today = datetime.now().strftime('%Y-%m-%d')

file_path = 'data/instagram_followers_foundation/daily.csv'
file_exists = os.path.exists(file_path)

# First, check if we already have today's data
already_recorded = False
if file_exists:
    with open(file_path, mode='r') as file:
        reader = csv.reader(file)
        next(reader, None)  # Skip header
        for row in reader:
            if row and row[0] == today:
                already_recorded = True
                break

# Only write if we haven't recorded today's data
if not already_recorded:
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        # Write the header if the file is empty or doesn't exist
        if not file_exists:
            writer.writerow(["date", "instagram_followers_foundation"])
        writer.writerow([today, profile.followers])
