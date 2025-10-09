import requests
import json
import threading
import csv
import sys
from concurrent.futures import ThreadPoolExecutor
from utils import setup_proxy, get_headers, disable_ssl_warnings, get_network_config, get_api_config, ensure_output_dir
from constants import DEFAULT_PATHS, DEFAULTS

# ================================================================
# INITIALIZATION
# ================================================================

# Setup proxy and disable SSL warnings
if not setup_proxy():
    sys.exit(1)

disable_ssl_warnings()

# ================================================================
# CONFIGURATION
# ================================================================

# Get the input file name from the user (expects a .txt file with one ID per line)
print(f"Available files in assets directory:")
import os
assets_dir = DEFAULT_PATHS['assets_dir']
if os.path.exists(assets_dir):
    files = [f for f in os.listdir(assets_dir) if f.endswith('.txt')]
    for file in files:
        print(f"  - {file}")

input_filename = input("Please enter the input file name (e.g., 'input_transactions.txt'): ").strip()

# If it's just a filename without path, look in the assets directory
if '/' not in input_filename:
    INPUT_FILE = f"{DEFAULT_PATHS['assets_dir']}/{input_filename}"
else:
    INPUT_FILE = input_filename

# File to write the output CSV to
OUTPUT_FILE = DEFAULT_PATHS['output_responses']

# Get API configuration and network settings
API_CONFIG = get_api_config()
HEADERS = get_headers()
network_config = get_network_config()
MAX_WORKERS = network_config['max_workers']

# ================================================================
# SCRIPT LOGIC
# ================================================================

# Shared list to store results and a lock for thread-safe updates
results = []
lock = threading.Lock()

def process_transaction(oma_id):
    """
    Constructs the API URL for a given OMA ID, makes the request,
    and records the reconciliation state from the response.
    """
    base_url = API_CONFIG["mandate_check"]["base_url"]
    endpoint_suffix = API_CONFIG["mandate_check"]["endpoint_suffix"]
    url = f"{base_url}{oma_id}{endpoint_suffix}"

    status_code = "Error"
    response_output = DEFAULTS['no_response']

    try:
        response = requests.get(url, headers=HEADERS, verify=False, timeout=network_config['timeout'])
        status_code = response.status_code

        if response.status_code == 200:
            try:
                # Parse the JSON and extract the reconciliation state
                data = response.json()
                response_output = data.get('data', {}).get('reconciliationState', DEFAULTS['reconciliation_state_not_found'])
            except json.JSONDecodeError:
                response_output = DEFAULTS['json_decode_error']
        else:
            # For non-200 responses, record the error text
            response_output = f"Body: {response.text}"

    except (requests.exceptions.RequestException, Exception) as e:
        response_output = DEFAULTS['no_response']
        # print(f"Error for {oma_id}: {e}") # Uncomment for debugging

    # Use a lock to safely append the result to the shared list
    with lock:
        results.append([oma_id, status_code, response_output])

    print(f"Processed: {oma_id}")

def main():
    """
    Main function to read OMA IDs from a text file, process them concurrently,
    and write the results to a new file.
    """
    oma_ids = []
    try:
        with open(INPUT_FILE, mode='r', encoding='utf-8') as f:
            # Read each line from the file, strip whitespace, and add to the list if it's not empty
            oma_ids = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: The input file '{INPUT_FILE}' was not found.")
        return

    if not oma_ids:
        print(f"No OMA IDs found in '{INPUT_FILE}'. No transactions to process.")
        return

    print(f"Starting to process {len(oma_ids)} transactions...")

    # Use a thread pool to execute all API calls concurrently
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(process_transaction, oma_ids)

    print("\nAll transactions processed. Writing results to file.")

    # Ensure output directory exists
    ensure_output_dir()

    # Write the final results to a CSV file
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        header = ["OMA_ID", "StatusCode", "ReconciliationState"]
        writer.writerow(header)
        writer.writerows(results)

    print(f"Results successfully written to '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    main()

