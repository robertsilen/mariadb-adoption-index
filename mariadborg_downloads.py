import json
import pandas as pd

data = json.load(open('mariadborg_downloads_raw.json', 'r'))
df = pd.DataFrame(data['result'])
monthly_totals = df.groupby('month')['no_dlds'].sum().reset_index()
monthly_totals['month'] = monthly_totals['month'].str[:-3]
monthly_totals = monthly_totals.sort_values('month', ascending=False)
monthly_totals.to_csv('mariadborg_downloads_monthly.csv', index=False)