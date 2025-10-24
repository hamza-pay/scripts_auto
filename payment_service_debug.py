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

# Show available .txt files and let user choose
from utils import show_available_assets, get_asset_file_path

print("Payment Service Debug API Processing")
print("===================================")

show_available_assets(['.txt'])

input_filename = input("Please enter the input file name containing transaction IDs (e.g., 'transaction_ids.txt'): ").strip()

# Get the full path to the input file
INPUT_FILE = get_asset_file_path(input_filename) if input_filename else DEFAULT_PATHS['input_transactions']
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

def process_transaction_id(transaction_id):
    """
    Constructs the API URL for payment service debug endpoint, makes a GET request, and records the response.
    """
    base_url = API_CONFIG['payment_service_debug']['base_url']
    endpoint_suffix = API_CONFIG['payment_service_debug']['endpoint_suffix']
    url = f"{base_url}{transaction_id}{endpoint_suffix}"

    status_code = "Error"
    response_output = DEFAULTS['no_response']

    try:
        response = requests.get(url, headers=HEADERS, verify=False, timeout=network_config['timeout'])
        status_code = response.status_code

        if response.status_code == 200:
            try:
                # Parse the JSON response and extract the executionState field
                data = response.json()
                response_output = data.get('data', {}).get('executionState', DEFAULTS['not_available'])
            except json.JSONDecodeError:
                response_output = DEFAULTS['json_decode_error']
        else:
            # For non-200 responses, record the status code and response text
            response_output = f"HTTP {response.status_code}: {response.text}"

    except requests.exceptions.Timeout:
        response_output = "Request timeout"
    except requests.exceptions.ConnectionError:
        response_output = "Connection error"
    except (requests.exceptions.RequestException, Exception) as e:
        response_output = f"Request failed: {str(e)}"

    # Use a lock to safely append the result to the shared list
    with lock:
        results.append([transaction_id, status_code, response_output])

    print(f"Processed: {transaction_id} - Status: {status_code}")

def main():
    """
    Main function to read transaction IDs and process them using the payment service debug API.
    """
    try:
        with open(INPUT_FILE, 'r') as f:
            transaction_ids = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: The file '{INPUT_FILE}' was not found.")
        return

    if not transaction_ids:
        print(f"The file '{INPUT_FILE}' is empty. No transaction IDs to process.")
        return

    print(f"Starting to process {len(transaction_ids)} transaction IDs using the payment service debug API...")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(process_transaction_id, transaction_ids)

    print("\nAll transaction IDs processed. Writing results to file.")

    # Ensure output directory exists
    ensure_output_dir()

    # Write the final results to a CSV file
    with open(OUTPUT_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        header = ["transaction_id", "status_code", "execution_state"]
        writer.writerow(header)
        writer.writerows(results)

    print(f"Results successfully written to '{OUTPUT_FILE}'.")
    print(f"Processed {len(results)} transaction IDs total.")

if __name__ == "__main__":
    main()