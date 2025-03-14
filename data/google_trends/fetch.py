from pytrends.request import TrendReq
import pandas as pd

# Set pandas option to handle future deprecation warning
pd.set_option('future.no_silent_downcasting', True)

# Initialize pytrends
pytrends = TrendReq(hl='en-US', tz=0)

# Define search term
kw_list = ["MariaDB"]

# Fetch interest over time for the past 5 years
timeframe = 'today 5-y'  # Last 5 years
geo = ''  # Global search
pytrends.build_payload(kw_list, cat=0, timeframe=timeframe, geo=geo, gprop='')

data = pytrends.interest_over_time()

# Remove "isPartial" column if it exists
if 'isPartial' in data.columns:
    data = data.drop(columns=['isPartial'])

# Handle data types explicitly
data = data.infer_objects(copy=False)

# Format data to show monthly values
data.index = data.index.to_period('M')  # Convert to monthly periods
data = data.groupby(data.index).mean()  # Aggregate by month

# Rename columns and reset index
data = data.reset_index()
data.columns = ['month', 'google_trends']
data['month'] = data['month'].astype(str)  # Convert to yyyy-mm format

# Save to CSV
data.to_csv("data/google_trends/monthly.csv", index=False)

print("Data saved to data/google_trends/monthly.csv")
