import pandas as pd
import time
import os
from utils import show_available_assets, get_asset_file_path

# --- Configuration ---
print("CSV Filter Script")
print("================")

# Show available CSV files in assets directory
available_files = show_available_assets(['.csv'])

if available_files:
    print("\nPlease select a CSV file to filter:")
    source_filename = input("Enter the filename (e.g., 'VIRALO.csv'): ").strip()
    source_file = get_asset_file_path(source_filename)
else:
    print("No CSV files found in assets directory!")
    exit(1)

# Output file configuration
output_filename = input("Enter output filename (e.g., 'filtered_data.csv'): ").strip()
if not output_filename.endswith('.csv'):
    output_filename += '.csv'
output_file = f'output/{output_filename}'

filter_column = 'eventdata_merchantid'
filter_value = 'VIRALOONLINE'
chunk_size = 100000  # Process 100,000 rows at a time
# -------------------

start_time = time.time()
print(f"Starting to filter '{source_file}'...")

# Use a flag to write the header only for the first chunk
is_first_chunk = True

# Create an iterator that reads the CSV in manageable chunks
# Strip whitespace from column names to handle CSV formatting issues
chunk_iterator = pd.read_csv(source_file, chunksize=chunk_size, low_memory=False)

# Clean column names for the first chunk to verify the fix
first_chunk = next(iter(pd.read_csv(source_file, chunksize=chunk_size, low_memory=False, nrows=1)))
first_chunk.columns = first_chunk.columns.str.strip()
if filter_column not in first_chunk.columns:
    print(f"Warning: Column '{filter_column}' not found!")
    print(f"Available columns: {list(first_chunk.columns)}")
    exit(1)

# Now create the actual iterator
chunk_iterator = pd.read_csv(source_file, chunksize=chunk_size, low_memory=False)

# Loop through each chunk
for i, chunk in enumerate(chunk_iterator):
    print(f"  - Processing chunk {i+1}...")
    
    # Strip whitespace from column names
    chunk.columns = chunk.columns.str.strip()
    
    # Filter the chunk for rows where the column matches the value
    filtered_chunk = chunk[chunk[filter_column] == filter_value]
    
    # If this is the first chunk, write to a new file with the header
    if is_first_chunk and not filtered_chunk.empty:
        filtered_chunk.to_csv(output_file, index=False, mode='w', header=True)
        is_first_chunk = False
    # For subsequent chunks, append to the file without the header
    elif not filtered_chunk.empty:
        filtered_chunk.to_csv(output_file, index=False, mode='a', header=False)

end_time = time.time()
print(f"\nFiltering complete! The new file is named '{output_file}'.")
print(f"Total time taken: {end_time - start_time:.2f} seconds.")