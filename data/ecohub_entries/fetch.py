# Counts the entries on the MariaDB Ecosystem Hub, https://ecohub.mariadb.org
# Uses the JSON catalog the site publishes (see https://ecohub.mariadb.org/llms.txt) and the same
# visibility filters as https://ecohub.mariadb.org/js/home.js, so the result equals the
# "N products across M categories" line on the home page.
#
# Exits with an error if any category fails to load: the site treats a failed category as empty,
# which here would record a false drop in the count.

import json
import sys
import urllib.request

BASE_URL = "https://ecohub.mariadb.org"
USER_AGENT = "mariadb-adoption-index/0.1"

def get_json(path):
    request = urllib.request.Request(BASE_URL + path, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)

def get_entry_count():
    categories = get_json("/categories.json")["categories"]
    visible = [
        c for c in categories
        if c.get("visible") is not False and c.get("type") not in ("sponsors", "new-entries")
    ]

    total = 0
    for category in visible:
        entries = get_json(category["file"])
        if not isinstance(entries, list):
            raise ValueError(f"{category['file']} is not a list")
        total += sum(1 for entry in entries if entry.get("visible") is not False)

    if total == 0:
        raise ValueError("No entries found")
    return total

if __name__ == "__main__":
    try:
        print(get_entry_count())
    except Exception as e:
        print(f"Error fetching Ecosystem Hub entries: {e}", file=sys.stderr)
        sys.exit(1)
