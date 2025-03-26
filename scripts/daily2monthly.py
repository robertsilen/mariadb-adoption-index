import pandas as pd
import sys

def dailymax2monthly(value):
    path = f'data/{value}/'
    try:
        # Try reading with explicit delimiter and error handling
        df_daily = pd.read_csv(path + 'daily.csv', 
                             header=0,
                             delimiter=',',
                             on_bad_lines='warn')
        
        df_daily['date'] = pd.to_datetime(df_daily['date'])
        df_daily['month'] = df_daily['date'].dt.strftime('%Y-%m')
        df_month_new = df_daily.groupby('month')[value].max().reset_index()
        print("New monthly data:")
        print(df_month_new)

        df_monthly_old = pd.read_csv(path + 'monthly.csv', header=0)
        df_monthly_old = df_monthly_old[['month', value]]
        print("\nExisting monthly data:")
        print(df_monthly_old)

        df_combined = pd.concat([df_monthly_old, df_month_new])
        df_combined = df_combined.drop_duplicates(subset=['month'], keep='last').sort_values('month').reset_index(drop=True)
        print("\nCombined data:")
        print(df_combined)

        df_combined.to_csv(path + 'monthly.csv', index=False)
        
    except Exception as e:
        print(f"Error processing files: {str(e)}")
        print("\nAttempting to debug daily.csv...")
        # Read the file line by line to identify problematic rows
        try:
            with open(path + 'daily.csv', 'r') as f:
                for i, line in enumerate(f, 1):
                    print(f"Line {i}: {line.strip()}, Fields: {len(line.strip().split(','))}")
        except Exception as read_error:
            print(f"Could not read daily.csv: {str(read_error)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python daily2monthly.py <value>")
        sys.exit(1)
    dailymax2monthly(sys.argv[1])
    