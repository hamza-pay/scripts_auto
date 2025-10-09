import pandas as pd
import os
from constants import DEFAULT_PATHS

# The name of your large CSV file
source_file = f'/Users/hamza.ansari/Misc/scripts/{DEFAULT_PATHS["assets_dir"]}/KUKU_VIRALO.csv'
# Number of rows per smaller file
chunk_size = 500000
# The prefix for the new files
file_prefix = 'KUKU_VIRALO'

# Ensure output directory exists
output_dir = f'/Users/hamza.ansari/Misc/scripts/{DEFAULT_PATHS["output_dir"]}'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Create an iterator that reads the CSV in chunks
chunk_iterator = pd.read_csv(source_file, chunksize=chunk_size)

# Loop through the chunks and save each one to a new file
for i, chunk in enumerate(chunk_iterator):
    output_file = f"{output_dir}/{file_prefix}_{i+1}.csv"
    print(f"Saving {output_file}...")
    chunk.to_csv(output_file, index=False)

print("Splitting complete!")