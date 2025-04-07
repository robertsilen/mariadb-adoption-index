import requests
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

USER_AGENT = "MariaDBStatsBot/1.0 (foundation@mariadb.org)"

def get_wikipedia_languages(qid="Q787177"):
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbgetentities",
        "ids": qid,
        "format": "json",
        "props": "sitelinks"
    }
    headers = {
        'User-Agent': USER_AGENT
    }

    response = requests.get(url, params=params, headers=headers)
    data = response.json()

    languages_and_titles = []
    if "entities" in data and qid in data["entities"]:
        sitelinks = data["entities"][qid]["sitelinks"]
        for site_id, site_data in sitelinks.items():
            if site_id.endswith("wiki"):  # Filter for Wikipedia sites
                lang_code = site_id.replace("wiki", "")
                title = site_data["title"]
                languages_and_titles.append({"lang":lang_code, "title":title})
    print("languages: ", languages_and_titles)
    return languages_and_titles


def get_pageview_stats(languages_and_titles, start_date, end_date):
    all_stats = []
    headers = {
        'User-Agent': USER_AGENT
    }
    
    for lang_title in languages_and_titles:
        lang = lang_title["lang"]
        title = lang_title["title"]
        url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/{lang}.wikipedia/all-access/all-agents/{title}/monthly/{start_date.strftime('%Y%m%d')}/{end_date.strftime('%Y%m%d')}"
        print(lang)
        try:
            response = requests.get(url, headers=headers)
            data = response.json()
            for item in data.get("items", []):
                stat = {
                    "lang": lang,
                    "title": title,
                    "views": item["views"],
                    "timestamp": item["timestamp"]
                }
                all_stats.append(stat)
        except Exception as e:
            print(f"Error fetching stats for {lang}:{title} - {str(e)}")
            continue
    return all_stats

def stats_to_csv(stats, output_path):
    # Convert the input stats to a DataFrame
    df = pd.DataFrame(stats)
    
    # Ensure timestamp is parsed correctly
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y%m%d00')
    
    # Group data by month and sum views
    df['month'] = df['timestamp'].dt.strftime('%Y-%m')
    grouped_df = df.groupby('month')['views'].sum().reset_index()
    
    # Rename the views column to wikipedia_views_all_langs
    grouped_df = grouped_df.rename(columns={'views': 'wikipedia_views_all_langs'})
    
    # Sort grouped data by month in descending order
    grouped_df = grouped_df.sort_values('month', ascending=False)
    
    # Print the grouped data for verification
    print("Total views by month:")
    print(grouped_df)
    
    # Save the grouped data to a CSV file
    grouped_df.to_csv(output_path, index=False)

# set time period
today = datetime.today()
end_date = today.replace(day=1) - timedelta(days=1)  # Last day of previous month
start_date = datetime(2023, 1, 1)  # Start from January 2024

langs = get_wikipedia_languages()
stats = get_pageview_stats(langs, start_date, end_date)
stats_to_csv(stats, "data/wikipedia_views_all_langs/monthly.csv")