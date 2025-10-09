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

# Show available CSV files and let user choose
from utils import show_available_assets, get_asset_file_path

print("Payments Transactions Processing")
print("===============================")

show_available_assets(['.csv'])

input_filename = input("Please enter the input CSV file name (e.g., 'input_data.csv'): ").strip()

# Get the full path to the input file
INPUT_FILE = get_asset_file_path(input_filename) if input_filename else DEFAULT_PATHS['input_data']
OUTPUT_FILE = DEFAULT_PATHS['output_responses']

# Get API configuration and network settings
API_CONFIG = get_api_config()
HEADERS = get_headers()
network_config = get_network_config()
MAX_WORKERS = network_config['max_workers']

# ================================================================
# SCRIPT LOGIC
# ================================================================

# Shared list to store results and a lock for thread-safe appends
results = []
lock = threading.Lock()

def make_api_call(service_name, id1, id2=None):
    """
    Makes a single API call and returns the parsed response.
    This is a helper function.
    """
    url = ""
    # --- Step 1: Configure the API call based on the service name ---
    if service_name == "hermes_status_check":
        base_url = API_CONFIG[service_name]["base_url"]
        url = f"{base_url}{id1}/{id2}" # Uses merchant_id and merchant_txn_id

    elif service_name == "payments_debug":
        base_url = API_CONFIG[service_name]["base_url"]
        endpoint_suffix = API_CONFIG[service_name]["endpoint_suffix"]
        url = f"{base_url}{id1}{endpoint_suffix}" # Uses payment_id

    else:
        return DEFAULTS['unknown_service']

    try:
        # --- Step 2: Make the API request ---
        response = requests.get(url, headers=HEADERS, verify=False, timeout=network_config['timeout'])

        if response.status_code == 200:
            try:
                data = response.json()
                # --- Step 3: Parse the response differently for each service ---
                if service_name == "hermes_status_check":
                    return data.get('message', DEFAULTS['message_not_found'])
                elif service_name == "payments_debug":
                    return data.get('data', {}).get('executionState', DEFAULTS['execution_state_not_found'])
            except json.JSONDecodeError:
                return DEFAULTS['json_decode_error']
        else:
            # For non-200 responses, return the status and error message
            return f"Error {response.status_code}: {response.text}"

    except (requests.exceptions.RequestException, Exception):
        # Handle network, timeout, or proxy errors
        return DEFAULTS['no_response']

def process_csv_row(row):
    """
    Processes a single row from the CSV file.
    It makes two sequential API calls (Hermes, then Payments) and combines the results.
    """
    # Get the required IDs from the row
    merchant_id = row.get('Merchant ID')
    merchant_txn_id = row.get('Merchant Transaction Id')
    payment_id = row.get('Payment Id')

    hermes_response = DEFAULTS['skipped']
    payments_response = DEFAULTS['skipped']

    # Call Hermes API if the required IDs are present
    if merchant_id and merchant_txn_id:
        hermes_response = make_api_call("hermes_status_check", merchant_id, merchant_txn_id)

    # Call Payments Debug API if the required ID is present
    if payment_id:
        payments_response = make_api_call("payments_debug", payment_id)

    # Prepare the final output row
    output_row = [
        payment_id or DEFAULTS['not_available'],
        merchant_txn_id or DEFAULTS['not_available'],
        hermes_response,
        payments_response
    ]

    # Safely append the result to the shared list
    with lock:
        results.append(output_row)

    print(f"Processed row for Payment ID: {payment_id or DEFAULTS['not_available']}")

def main():
    """
    Main function to read a CSV, process each row concurrently,
    and write the combined results to a new file.
    """
    rows_to_process = []
    try:
        with open(INPUT_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Read all rows into a list to be processed
            rows_to_process = list(reader)

    except FileNotFoundError:
        print(f"Error: The input file '{INPUT_FILE}' was not found.")
        return
    except KeyError as e:
        print(f"Error: Missing required column in CSV: {e}. Please ensure columns 'Merchant ID', 'Merchant Transaction Id', and 'Payment Id' exist.")
        return

    if not rows_to_process:
        print(f"The file '{INPUT_FILE}' is empty or no valid data found. No tasks to process.")
        return

    print(f"Starting to process {len(rows_to_process)} rows...")

    # Use a thread pool to process each CSV row in parallel
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(process_csv_row, rows_to_process)

    print("\nAll rows processed. Writing results to file.")

    # Ensure output directory exists
    ensure_output_dir()

    # Write the final results to a new CSV file
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Write the new header as requested
        header = ["Payment Id", "Merchant Transaction Id", "Hermes Response", "Payments Debug Response"]
        writer.writerow(header)
        writer.writerows(results)

    # Provide a final confirmation message to the user
    print(f"Results successfully written to '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    main()
