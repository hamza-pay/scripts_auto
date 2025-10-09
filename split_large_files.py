import pandas as pd
import os
from constants import DEFAULT_PATHS
from utils import show_available_assets, get_asset_file_path, ensure_output_dir

print("Large File Splitter")
print("==================")

# Show available CSV files in assets directory
available_files = show_available_assets(['.csv'])

if available_files:
    file_name = input("Enter the name of the large CSV file (with .csv extension): ").strip()
else:
    print("No CSV files found in assets directory!")
    exit(1)

# The name of your large CSV file
source_file = get_asset_file_path(file_name)
# Number of rows per smaller file
chunk_size = 500000
# The prefix for the new files
file_prefix = file_name.replace('.csv', '')

# Ensure output directory exists
output_dir = DEFAULT_PATHS["output_dir"]
ensure_output_dir()

# Create an iterator that reads the CSV in chunks
chunk_iterator = pd.read_csv(source_file, chunksize=chunk_size)

# Loop through the chunks and save each one to a new file
for i, chunk in enumerate(chunk_iterator):
    output_file = f"{output_dir}/{file_prefix}_{i+1}.csv"
    print(f"Saving {output_file}...")
    chunk.to_csv(output_file, index=False)

print("Splitting complete!")