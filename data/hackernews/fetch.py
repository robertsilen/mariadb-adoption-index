import requests
import pandas as pd
import re
from collections import defaultdict
from datetime import datetime

# API Endpoint
API_URL = "https://hn.algolia.com/api/v1/search_by_date"
QUERY = "mariadb"

# Store results
monthly_mentions = defaultdict(int)

def contains_mariadb(item):
    """Check if 'mariadb' appears as a word in title, url, or story_text"""
    # Combine all text fields
    text = ' '.join([
        item.get('title') or '',
        item.get('url') or '',
        item.get('story_text') or ''
    ]).lower()
    # Match 'mariadb' as a word (not part of another word)
    return bool(re.search(r'\bmariadb\b', text))

page = 0
while True:
    try:
        response = requests.get(API_URL, params={"query": QUERY, "tags": "story", "page": page})
        response.raise_for_status()
        data = response.json()
        
        if not data.get("hits"):
            break
        
        for item in data["hits"]:
            if not contains_mariadb(item):
                continue
            created_at = item.get("created_at")
            if created_at:
                try:
                    month = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m")
                except ValueError:
                    month = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m")
                monthly_mentions[month] += 1
        
        print(f"Processed page {page}, total mentions so far: {sum(monthly_mentions.values())}")
        page += 1
    except Exception as e:
        print(f"Stopping due to error: {e}")
        break

# Convert to DataFrame
monthly_df = pd.DataFrame(sorted(monthly_mentions.items(), key=lambda x: x[0]), 
                         columns=["month", "hackernews"])

# Save to CSV
monthly_df.to_csv("data/hackernews/monthly.csv", index=False)

print("Saved to monthly.csv")