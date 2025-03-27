import pandas as pd
import sys

def dailymax2monthly(value):
    path = f'data/{value}/'
    try:
        # Read daily data with better error handling and skip empty lines
        df_daily = pd.read_csv(path + 'daily.csv', 
                             header=0,
                             delimiter=',',
                             on_bad_lines='warn',
                             skip_blank_lines=True)
        
        # Validate that required columns exist
        if 'date' not in df_daily.columns:
            raise ValueError("'date' column not found in daily.csv")
        if value not in df_daily.columns:
            raise ValueError(f"'{value}' column not found in daily.csv")
            
        # Clean the dataframe by dropping any rows with NaN values
        df_daily = df_daily.dropna(subset=['date', value])
        
        # Convert date and sort by it first
        df_daily['date'] = pd.to_datetime(df_daily['date'])
        df_daily = df_daily.sort_values('date')  # Sort by full date
        df_daily['month'] = df_daily['date'].dt.strftime('%Y-%m')
        
        # Group by month and take the last value, is sorted by date already
        df_month_new = df_daily.groupby('month')[value].last().reset_index()
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
        try:
            with open(path + 'daily.csv', 'r') as f:
                lines = [line.strip() for line in f if line.strip()]  # Skip empty lines
                for i, line in enumerate(lines, 1):
                    print(f"Line {i}: {line}, Fields: {len(line.split(','))}")
        except Exception as read_error:
            print(f"Could not read daily.csv: {str(read_error)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python daily2monthly.py <value>")
        sys.exit(1)
    value = sys.argv[1]
    dailymax2monthly(value)
    