import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt


# 1. Read create_index_weights.csv and plot weights as a pie chart
weights = pd.read_csv('index/create_index_weights.csv')
plt.figure(figsize=(10, 8))
plt.pie(weights['weight'], labels=weights['label'], autopct='%1.1f%%', startangle=140, textprops={'fontsize': 8})
plt.title('Weights Distribution')
plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
plt.savefig('index/mariadb_adoption_index_weights.png', dpi=100)  # Save the pie chart as a PNG file with lower resolution
plt.close()  # Close the plot to free up memory

# 2. Combine the monthly data from csv files using merge
combined_data = pd.DataFrame(columns=['month'])
for index, row in weights.iterrows():
    monthly_data = pd.read_csv(f'data/{row['path']}/monthly.csv')
    combined_data = combined_data.merge(
        monthly_data,
        on='month',
        how='outer'
    )
    combined_data = combined_data.fillna(0).astype({col: 'int' for col in combined_data.columns if col != 'month'})
# 3. Calculate index values for each column (excluding 'month') by adding a column _index for each column, and set the baseline to 2024-01
baseline_date = '2024-01'
for column in combined_data.columns:
    if column != 'month':
        baseline_value = combined_data[combined_data['month'] == baseline_date][column].iloc[0]
        combined_data[f'{column}_index'] = combined_data[column] / baseline_value * 100

# 4. Calculate the weighted index by multiplying each index column by its weight and summing the results
weights_sum = weights['weight'].sum()
combined_data['weighted_index'] = 0
for index, row in weights.iterrows():
    column_name = f"{row['path']}_index"
    combined_data['weighted_index'] += combined_data[column_name] * row['weight']
combined_data['weighted_index'] = (combined_data['weighted_index'] / weights_sum).astype(int)

# 5. Prepare the final table with the weighted index and columns with values
# and save to a csv file
combined_data = combined_data.loc[:, ~combined_data.columns.str.endswith('_index') | (combined_data.columns == 'weighted_index')]
# Move weighted_index to be the first column after 'month'
combined_data = combined_data[['month', 'weighted_index'] + [col for col in combined_data.columns if col not in ['month', 'weighted_index']]]

# Replace the column names with the labels from the weights DataFrame
for index, row in weights.iterrows():
    if row['path'] in combined_data.columns:
        combined_data.rename(columns={row['path']: row['label']}, inplace=True)
combined_data.rename(columns={'weighted_index': 'Weighted Index'}, inplace=True)
# Filter to last 12 months and baseline month
current_date = datetime.now()
previous_month = (current_date - timedelta(days=current_date.day)).replace(day=1)
months_to_include = [baseline_date] + [(previous_month - timedelta(days=30 * i)).strftime('%Y-%m') for i in range(12)]
filtered_data = combined_data[combined_data['month'].isin(months_to_include)]
# Transpose the DataFrame and save to a csv file
filtered_data = filtered_data.set_index('month').T
# Format the filtered_data values with thousand separators
formatted_data = filtered_data.map(lambda x: f"{int(x):,}" if isinstance(x, (int, float)) else x)  # Handle numpy.int64



filtered_data.to_csv('index/mariadb_adoption_index_table_12m.csv')
# and save the table to a PNG file
plt.figure(figsize=(10, 5))
plt.axis('off') 
formatted_data = formatted_data.reset_index() # Reset index to include it in the values

# trying to add weights as the first column to the final table
#weights_with_empty_row = pd.Series([''] + weights['weight'].astype(str).values.tolist())  # Change weights to strings
#filtered_data = filtered_data.insert(0, 'Weight', weights_with_empty_row.values)  # Add weights as the first column

cell_text = formatted_data.values  
col_labels = [''] + list(filtered_data.columns)  # Add empty cell as the first column label
table = plt.table(cellText=cell_text, colLabels=col_labels, cellLoc='right', loc='center', colColours=['#f5f5f5']*len(col_labels))
table.auto_set_column_width([0])  # Set the width of the first column automatically
table.scale(1.2, 1)  # Scale the table for better visibility
plt.savefig('index/mariadb_adoption_index_table_12m.png', bbox_inches='tight', dpi=300)  # Save the table as a PNG file
plt.close()  # Close the plot to free up memory

# 7. Plot the weighted_index row
filtered_data = filtered_data.drop(columns=['2024-01'], errors='ignore')  # Drop the column for the baseline 2024-01
plt.figure(figsize=(10, 5))
plt.plot(filtered_data.columns, filtered_data.loc['Weighted Index'], marker='o')  # Convert x-axis values to strings
plt.title('Weighted Index Over Time')
plt.xlabel('Month')
plt.ylabel('Weighted Index')
plt.xticks(rotation=45)
plt.grid()
plt.tight_layout()
plt.savefig('index/mariadb_adoption_index_chart_12m.png')  # Save the plot as a PNG file
