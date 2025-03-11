import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Read all monthly files in the current directory and combine them into a single dataframe
monthly_files = list(Path('.').glob('*_monthly.csv'))
dfs = []
for file in monthly_files:
    df = pd.read_csv(file)
    if 'month' in df.columns:
        # Convert numeric columns to integers by dropping decimals
        numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
        for col in numeric_columns:
            if col != 'month':  # Keep month column as is
                df[col] = df[col].round().astype('Int64')  # Int64 handles NaN values
        dfs.append(df)

combined_df = dfs[0]
for df in dfs[1:]:
    combined_df = pd.merge(combined_df, df, on='month', how='outer')
combined_df = combined_df.sort_values('month')

print("Combined data:")
print(combined_df)

# Create monthly_values.csv with base month and last 12 months
monthly_values = pd.DataFrame()
base_month = combined_df[combined_df['month'] == '2024-01'].iloc[0]
monthly_values['2024-01'] = base_month.drop('month')
last_12_months = combined_df[
    (combined_df['month'] >= '2024-03') & 
    (combined_df['month'] <= '2025-02')
].copy()
for _, row in last_12_months.iterrows():
    month = row['month']
    monthly_values[month] = row.drop('month')
monthly_values.to_csv('monthly_values.csv')

# Create indexed versions of each numeric column
numeric_columns = combined_df.select_dtypes(include=['float64', 'int64']).columns
indexed_df = combined_df.copy()

for col in numeric_columns:
    if col != 'month':  # Skip the month column
        # Get the value for January 2024
        base_value = combined_df[combined_df['month'] == '2024-01'][col].iloc[0]
        # Calculate index values relative to January 2024
        indexed_df[f'{col}_index'] = (combined_df[col] / base_value * 100).round(1)

print("\nIndexed data (January 2024 = 100):")
print(indexed_df)

# Filter for last 12 months ending in February 2025
last_12_months_df = indexed_df[
    (indexed_df['month'] >= '2024-03') & 
    (indexed_df['month'] <= '2025-02')
].copy()

# Add column with average of columns ending in _indexed
last_12_months_df['average_index'] = last_12_months_df[[col for col in last_12_months_df.columns if col.endswith('_index')]].mean(axis=1)
print("\nIndex data (January 2024 = 100):")
print(last_12_months_df)

#plot average_index and save to png file
plt.figure(figsize=(12, 6))
plt.plot(last_12_months_df['month'], last_12_months_df['average_index'], marker='o', label='Average Index')
plt.title('Average Index Over Time (March 2024 - February 2025)')
plt.xlabel('Month')
plt.ylabel('Index Value')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('monthly_index.png')