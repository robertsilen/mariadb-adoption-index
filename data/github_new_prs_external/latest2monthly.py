import pandas as pd

df = pd.read_csv('data/github_new_prs_external/since-2023-01-01.csv')
print(f"Total number of PRs: {len(df)}")

df = df[df['labels'].str.contains("External Contribution", na=False)]
print(f"Total number of PRs labeled 'External Contribution': {len(df)}")

df['month'] = pd.to_datetime(df['created_date']).dt.to_period('M')
monthly_counts = df.groupby('month').size().reset_index(name='github_new_prs_external')

monthly_counts = monthly_counts.sort_values(by='month', ascending=False)

monthly_counts.to_csv('data/github_new_prs_external/monthly.csv', index=False)
print("Monthly counts saved to monthly.csv")