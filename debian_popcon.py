import json
import pandas as pd

# Read the JSON data
with open('debian_popcon_raw.json', 'r') as f:
    data = json.load(f)

mariadb_data = pd.DataFrame.from_dict(data['mariadb-server'], orient='index')# Calculate total installations per date
mariadb_data['total'] = mariadb_data['no_files'] + mariadb_data['old'] + mariadb_data['recent']
mariadb_data.index = pd.to_datetime(mariadb_data.index)

monthly_totals = mariadb_data['total'].resample('ME').sum()
monthly_df = monthly_totals.reset_index()
monthly_df.columns = ['month', 'debian_popcon']
monthly_df['month'] = monthly_df['month'].dt.strftime('%Y-%m')
monthly_df = monthly_df.sort_values('month', ascending=False)
monthly_df.to_csv('debian_popcon_monthly.csv', index=False)