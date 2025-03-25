import pandas as pd
import sys

def delta2monthly(value):
    path = f'data/{value}/'
    df_daily = pd.read_csv(path + 'daily.csv', header=0)

    df_daily['date'] = pd.to_datetime(df_daily['date'])
    df_daily['month'] = df_daily['date'].dt.strftime('%Y-%m')
    df_month_new = df_daily.groupby('month')[value].max().reset_index()
    print(df_month_new)

    df_month_new[value] = df_month_new[value] - df_month_new[value].shift(1)
    print(df_month_new)

    df_monthly_old = pd.read_csv(path + 'monthly.csv', header=0)
    df_monthly_old = df_monthly_old[['month', value]]
    print(df_monthly_old)

    df_combined = pd.concat([df_monthly_old, df_month_new])
    df_combined = df_combined.drop_duplicates(subset=['month'], keep='last').sort_values('month').reset_index(drop=True)
    print(df_combined)

    df_combined.to_csv(path + 'monthly.csv', index=False)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python delta2monthly.py <value>")
        sys.exit(1)
    delta2monthly(sys.argv[1])
    