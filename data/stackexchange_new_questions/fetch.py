import requests
import pandas as pd
from datetime import datetime

def get_mariadb_questions_by_month():
    # Base URL for the Stack Exchange API
    url = "https://api.stackexchange.com/2.3/questions"

    # Parameters for the API request
    params = {
        "site": "stackoverflow",  # Specify Stack Overflow
        "tagged": "mariadb",    # Filter by the 'mariadb' tag
        "pagesize": 100,          # Maximum number of results per page
        "order": "desc",         # Order by ascending creation date (to get older results first)
        "sort": "creation"       # Sort by creation date
    }

    all_questions = []
    has_more = True
    page = 1

    while has_more:
        print(f"Fetching page {page}")
        params["page"] = page
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            all_questions.extend(data.get("items", []))
            has_more = data.get("has_more", False)
            page += 1
        else:
            print(f"Failed to fetch data: {response.status_code} - {response.reason}")
            print(f"Requested URL: {response.url}")
            print(f"Parameters: {params}")
            print(f"Response text: {response.text}")
            break

    return all_questions

def save_to_monthly_csv(questions):
    # Convert the data into a DataFrame
    df = pd.DataFrame(questions)

    # Convert 'creation_date' from UNIX timestamp to datetime
    df['creation_date'] = pd.to_datetime(df['creation_date'], unit='s')

    # Group by year and month and count questions
    df['year_month'] = df['creation_date'].dt.strftime('%Y-%m')
    monthly_counts = df.groupby('year_month').size().reset_index()
    
    # Rename columns to match required format
    monthly_counts.columns = ['month', 'stackexchange_new_questions']
    
    # Sort monthly counts by newest date first
    monthly_counts = monthly_counts.sort_values(by='month', ascending=False)

    # Save results to CSV
    monthly_counts.to_csv('data/stackexchange_new_questions/monthly.csv', index=False)
    print("Data has been saved to 'monthly.csv'.")

# Process the result
questions = get_mariadb_questions_by_month()
save_to_monthly_csv(questions)
