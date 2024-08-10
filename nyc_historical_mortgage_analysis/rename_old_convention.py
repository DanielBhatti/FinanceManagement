import os
import re

dir_path = r"C:\Users\bhatt\repos\nyc_historical_mortgage_analysis\mortgage_data_raw"

for dirpath, subdir, filenames in os.walk(dir_path):
    for filename in filenames:
        # Check if the filename matches the specified pattern
        match = re.match(r"sales_(.*?)_(\d{2})\.xls", filename)
        if match:
            # Extract the borough and year
            borough, year = match.groups()
            
            # Construct the new filename
            new_filename = f"20{year}_{borough}.xls"
            
            # Full path for old and new filenames
            old_file = os.path.join(dirpath, filename)
            new_file = os.path.join(dirpath, new_filename)

            # Rename the file
            os.rename(old_file, new_file)
            print(f"Renamed '{old_file}' to '{new_file}'")


for dirpath, subdir, filenames in os.walk(dir_path):
    for filename in filenames:
        # Check if the filename matches the specified pattern
        match = re.match(r"sales_(\d{4})_(.*?)\.xls", filename)
        if match:
            # Extract the borough and year
            year, borough = match.groups()
            
            # Construct the new filename
            new_filename = f"{year}_{borough}.xls"
            
            # Full path for old and new filenames
            old_file = os.path.join(dirpath, filename)
            new_file = os.path.join(dirpath, new_filename)

            # Rename the file
            os.rename(old_file, new_file)
            print(f"Renamed '{old_file}' to '{new_file}'")


for dirpath, subdir, filenames in os.walk(dir_path):
    for filename in filenames:
        # Check if the filename matches the specified pattern
        match = re.match(r"(\d{4})_(.*?)\.xlsx?", filename)
        if match:
            new_filename = filename.replace("staten_island", "si").replace("statenisland", "si")
            
            # Full path for old and new filenames
            old_file = os.path.join(dirpath, filename)
            new_file = os.path.join(dirpath, new_filename)

            # Rename the file
            os.rename(old_file, new_file)
            print(f"Renamed '{old_file}' to '{new_file}'")

