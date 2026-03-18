import pandas as pd
import os
import sys

# Takes daily values and appends/merges into existing monthly data.
# Mode: "last" = use last value of each month; "cumulative" = use (last - first) in month (for cumulative daily series).
def daily2monthly(value, cumulative=False):
    path = f'data/{value}/'
    try:
        os.makedirs(path, exist_ok=True)

        daily_path = os.path.join(path, 'daily.csv')
        monthly_path = os.path.join(path, 'monthly.csv')

        # If daily.csv doesn't exist yet, create it and exit successfully.
        # We can't compute monthly from nothing, but we also don't want workflows to fail on first run.
        if not os.path.exists(daily_path):
            with open(daily_path, 'w', encoding='utf-8') as f:
                f.write(f"date,{value}\n")
            print(f"Created missing {daily_path}. No monthly update performed.")
            return

        # Ensure monthly.csv exists so merge/write is always safe.
        if not os.path.exists(monthly_path):
            with open(monthly_path, 'w', encoding='utf-8') as f:
                f.write(f"month,{value}\n")

        # Read daily data with better error handling and skip empty lines
        df_daily = pd.read_csv(daily_path, 
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
        
        if cumulative:
            # For cumulative series: monthly = last value in month - first value in month (pulls during that month)
            grp = df_daily.groupby('month')[value]
            df_month_new = (grp.last() - grp.first()).reset_index()
        else:
            # Default: take last value of each month
            df_month_new = df_daily.groupby('month')[value].last().reset_index()
        print("New monthly data:")
        print(df_month_new)

        df_monthly_old = pd.read_csv(monthly_path, header=0)
        df_monthly_old = df_monthly_old[['month', value]]
        print("\nExisting monthly data:")
        print(df_monthly_old)

        df_combined = pd.concat([df_monthly_old, df_month_new])
        df_combined = df_combined.drop_duplicates(subset=['month'], keep='last').sort_values('month').reset_index(drop=True)
        print("\nCombined data:")
        print(df_combined)

        df_combined.to_csv(monthly_path, index=False)
        
    except Exception as e:
        print(f"Error processing files: {str(e)}")
        print("\nAttempting to debug daily.csv...")
        try:
            with open(os.path.join(path, 'daily.csv'), 'r') as f:
                lines = [line.strip() for line in f if line.strip()]  # Skip empty lines
                for i, line in enumerate(lines, 1):
                    print(f"Line {i}: {line}, Fields: {len(line.split(','))}")
        except Exception as read_error:
            print(f"Could not read daily.csv: {str(read_error)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python daily2monthly.py <value> [--cumulative]")
        print("  --cumulative  for cumulative daily series: monthly = last - first in month (e.g. docker_official_image_pulls)")
        sys.exit(1)
    value = sys.argv[1]
    cumulative = "--cumulative" in sys.argv
    daily2monthly(value, cumulative=cumulative)
