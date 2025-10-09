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

# File paths
INPUT_FILE = DEFAULT_PATHS['input_transactions']
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

def process_transaction(args):
    """
    Constructs the API URL, makes a GET request, and records the response.
    This function now accepts a tuple of arguments.
    """
    transaction_id, base_url, endpoint_suffix, service_choice = args
    url = f"{base_url}{transaction_id}{endpoint_suffix}"

    status_code = "Error"
    response_output = DEFAULTS['no_response']

    try:
        response = requests.get(url, headers=HEADERS, verify=False, timeout=network_config['timeout'])
        status_code = response.status_code

        if response.status_code == 200:
            if service_choice == 'hermes':
                try:
                    # For Hermes, parse the JSON and extract the reconciliation state
                    data = response.json()
                    response_output = data.get('data', {}).get('reconciliationState', DEFAULTS['reconciliation_state_not_found'])
                except json.JSONDecodeError:
                    response_output = DEFAULTS['json_decode_error']
            else:
                # For 'ro', keep the full response body
                response_output = json.dumps(response.json())
        else:
            # For non-200 responses, record the status code and text
            response_output = f"Body: {response.text}"

    except (requests.exceptions.RequestException, Exception) as e:
        response_output = DEFAULTS['no_response']
        # Optional: Print the error for debugging
        # print(f"Error for {transaction_id}: {e}")

    # Use a lock to safely append the result to the shared list
    with lock:
        results.append([transaction_id, status_code, response_output])

    print(f"Processed: {transaction_id}")

def main():
    """
    Main function to handle user input, read transactions, and process them.
    """
    # Prompt the user for the service choice
    while True:
        service_choice = input("Please enter Service (hermes or ro): ").lower().strip()
        if service_choice in API_CONFIG:
            break
        elif service_choice == "exit":
            print("Exiting the script.")
            return
        print("Invalid service. Please enter 'hermes' or 'ro'.")

    base_url = API_CONFIG[service_choice]["base_url"]
    endpoint_suffix = API_CONFIG[service_choice]["endpoint_suffix"]

    try:
        with open(INPUT_FILE, 'r') as f:
            transactions = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: The file '{INPUT_FILE}' was not found.")
        return

    if not transactions:
        print(f"The file '{INPUT_FILE}' is empty. No transactions to process.")
        return

    print(f"Starting to process {len(transactions)} transactions using the '{service_choice}' service...")

    # Create a list of tuples for the executor, passing the service_choice to each task
    tasks = [(txn_id, base_url, endpoint_suffix, service_choice) for txn_id in transactions]

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(process_transaction, tasks)

    print("\nAll transactions processed. Writing results to file.")

    # Ensure output directory exists
    ensure_output_dir()

    # Write the final results to a CSV file
    with open(OUTPUT_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        # Use a more descriptive header for the third column based on the service
        header = ["transactionId", "statusCode", "reconciliationState" if service_choice == 'hermes' else "responseBody"]
        writer.writerow(header)
        writer.writerows(results)

    print(f"Results successfully written to '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    main()