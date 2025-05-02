import pandas as pd
import os

# Read the CSV file
df = pd.read_csv('data/docker_official_image_pulls/daily.csv')

# Convert date column to datetime
df['date'] = pd.to_datetime(df['date'])

# Set date as index and resample to monthly frequency, taking the last value of each month
monthly_data = df.set_index('date').resample('M').last()

# Calculate the delta between consecutive months
monthly_data['delta'] = monthly_data['docker_official_image_pulls'].diff()

# Get the last two months' data
last_month = monthly_data.index[-2]
two_months_ago = monthly_data.index[-3]

# Store the delta value
delta = int(monthly_data.loc[last_month, 'delta'])

delta_dict = {
    'month': last_month.strftime('%Y-%m'),
    'docker_official_image_pulls': delta,
}

# Print the results
print("delta for previous month calculated from daily.csv:", delta_dict)

# Ensure the file ends with a newline before appending
monthly_file = 'data/docker_official_image_pulls/monthly.csv'
if os.path.exists(monthly_file):
    with open(monthly_file, 'a') as f:
        if f.tell() > 0:  # if file is not empty
            f.write('\n')

# Append the new row to monthly.csv
pd.DataFrame([delta_dict]).to_csv(monthly_file, mode='a', header=False, index=False)

print("delta for previous month appended to monthly.csv")