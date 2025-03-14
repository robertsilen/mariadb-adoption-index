import pandas as pd

df_all = pd.read_csv('data/github_new_prs_external/since-2023-01-01.csv').fillna('')
df_all['month'] = pd.to_datetime(df_all['created_date']).dt.to_period('M')
df = df_all[df_all['labels'].str.contains("External Contribution", na=False)]
print(f"Data time period: {df_all['month'].min()} - {df_all['month'].max()}")
print(f"Total PRs: {len(df_all)}")
print("PRs with label External Contribution: ", len(df))

df = df.sort_values('month')
all_months = df['month'].unique()
all_months = sorted(all_months) 

results = pd.DataFrame()
results['month'] = all_months
unique_users_counts = []

for month in all_months:
    start_month = month - 11 
    window_data = df[(df['month'] >= start_month) & (df['month'] <= month)]
    unique_count = window_data['creator_username'].nunique()
    unique_users_counts.append(unique_count)
    print(f"{window_data['month'].min()} - {window_data['month'].max()}: PRs: {len(window_data)}, Unique Contributors: {unique_count}")
    #print(window_data['creator_username'].unique())

results['unique_users_12m'] = unique_users_counts
results['month'] = results['month'].astype(str)
results = results.sort_values('month', ascending=False)
results.to_csv('data/github_new_prs_unique_contributors/monthly.csv', index=False)
