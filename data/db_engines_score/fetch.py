import requests
import re
from bs4 import BeautifulSoup

def fetch_mariadb_stats():
    # URL for MariaDB's DB-Engines page
    url = "https://db-engines.com/en/system/MariaDB"
    
    try:
        # Send GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Convert the HTML to text
        text_content = soup.get_text()
        
        # Use regex to find the score
        score_pattern = r"Score\s*(\d+\.\d+)"
        score_match = re.search(score_pattern, text_content)
        
        # Use regex to find the ranks
        rank_pattern = r"Rank\s*#(\d+)\s*Overall.*?#(\d+)\s*Relational DBMS"
        rank_match = re.search(rank_pattern, text_content, re.DOTALL)
        
        results = {}
        
        if score_match:
            results['score'] = float(score_match.group(1))
            
        if rank_match:
            results['overall_rank'] = int(rank_match.group(1))
            results['rdbms_rank'] = int(rank_match.group(2))
            
        return results if results else None
            
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

if __name__ == "__main__":
    stats = fetch_mariadb_stats()
    if stats:
        print(f"MariaDB DB-Engines Stats:")
        print(f"Score: {stats.get('score', 'N/A')}")
        print(f"Overall Rank: #{stats.get('overall_rank', 'N/A')}")
        print(f"RDBMS Rank: #{stats.get('rdbms_rank', 'N/A')}")
    else:
        print("Failed to fetch MariaDB stats")
