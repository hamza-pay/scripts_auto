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

print("Refunds Housekeeping API Processing")
print("==================================")

show_available_assets(['.txt'])

input_filename = input("Please enter the input file name containing refund IDs (e.g., 'refund_ids.txt'): ").strip()

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

def process_refund_id(refund_id):
    """
    Constructs the API URL for refunds housekeeping endpoint, makes a GET request, and records the response.
    """
    base_url = API_CONFIG['refunds_housekeeping']['base_url']
    url = f"{base_url}{refund_id}"

    status_code = "Error"
    response_output = DEFAULTS['no_response']

    try:
        response = requests.get(url, headers=HEADERS, verify=False, timeout=network_config['timeout'])
        status_code = response.status_code

        if response.status_code == 200:
            try:
                # Parse the JSON response and extract the state field
                data = response.json()
                response_output = data.get('state', DEFAULTS['not_available'])
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
        results.append([refund_id, status_code, response_output])

    print(f"Processed: {refund_id} - Status: {status_code}")

def main():
    """
    Main function to read refund IDs and process them using the refunds housekeeping API.
    """
    try:
        with open(INPUT_FILE, 'r') as f:
            refund_ids = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: The file '{INPUT_FILE}' was not found.")
        return

    if not refund_ids:
        print(f"The file '{INPUT_FILE}' is empty. No refund IDs to process.")
        return

    print(f"Starting to process {len(refund_ids)} refund IDs using the refunds housekeeping API...")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(process_refund_id, refund_ids)

    print("\nAll refund IDs processed. Writing results to file.")

    # Ensure output directory exists
    ensure_output_dir()

    # Write the final results to a CSV file
    with open(OUTPUT_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        header = ["refund_id", "status_code", "state"]
        writer.writerow(header)
        writer.writerows(results)

    print(f"Results successfully written to '{OUTPUT_FILE}'.")
    print(f"Processed {len(results)} refund IDs total.")

if __name__ == "__main__":
    main()