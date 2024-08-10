import pandas as pd
import os
import re

def find_header_row(file_path):
    # Try reading only the first few rows of the file
    try:
        df = pd.read_excel(file_path, nrows=10)  # Adjust the number of rows as needed
        for i, row in df.iterrows():
            if 'BOROUGH' in row.values or 'BOROUGH\n' in row.values:  # Check for a key column name
                return i + 1
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return None

def read_data(file_path):
    header_row = find_header_row(file_path)
    if header_row is not None:
        df = pd.read_excel(file_path, header=header_row)
        return df
    else:
        print(f"Header not found in {file_path}")
        return None

# Directory containing your files
raw_data_dir_path = r'C:\Users\bhatt\repos\nyc_historical_mortgage_analysis\mortgage_data_raw'
csv_dir_path = r"C:\Users\bhatt\repos\nyc_historical_mortgage_analysis\mortgage_data_csv"

pattern = r"(\d{4})_(queens|manhattan|bronx|brooklyn|si)\.xls"

for filename in os.listdir(raw_data_dir_path):
    if (filename.endswith('.xls') or filename.endswith('.xlsx')) and re.match(pattern, filename):
        file_path = os.path.join(raw_data_dir_path, filename)
        # Define the CSV file name (same as original but with .csv)
        base_name, _ = os.path.splitext(filename)
        csv_filename = base_name + '.csv'
        csv_file_path = os.path.join(csv_dir_path, csv_filename)
        if os.path.exists(csv_file_path):
            continue
        print(file_path)
        df = read_data(file_path)  # Assuming read_data returns a cleaned DataFrame
        df.columns = [col.replace('\n', '').strip() for col in df.columns]
        if df is not None:
            df['SALE DATE'] = pd.to_datetime(df['SALE DATE'])

            # Save the DataFrame to a CSV file
            df.to_csv(csv_file_path, index=False)
            print(f"Saved to {csv_file_path}")
