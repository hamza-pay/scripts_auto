# PhonePe API Scripts

This directory contains Python scripts for interacting with PhonePe APIs, organized with proper separation of configuration, constants, and data files.

## Project Structure

```
scripts/
├── assets/                          # Input data files
│   ├── input_transactions.txt
│   ├── input_data.csv
│   └── .gitkeep
├── output/                          # Output/result files
│   ├── api_responses.csv
│   └── .gitkeep
├── constants.py                     # All URLs, endpoints, and constants
├── utils.py                        # Utility functions and environment handling
├── .env.template                   # Environment template file
├── .env.sample                     # Sample environment file
├── accounting_reversal_anomaly.py  # Reversal anomaly detection script
├── accounting_subscription.py       # Subscription management script
├── forward_anomaly_v1.py           # Forward anomaly detection v1
├── payments_transactions_v1.py     # Payment transaction processing v1
└── split_large_files.py           # Utility to split large CSV files
```

## Setup

1. **Environment Configuration**: Copy the environment template and add your credentials:
   ```bash
   cp .env.template .env
   ```

2. **Edit the .env file** with your actual authorization token:
   ```bash
   AUTHORIZATION_TOKEN=your-actual-jwt-token-here
   ```

3. **Input Files**: Place your input files in the `assets/` directory:
   - `input_transactions.txt` - One transaction ID per line
   - `input_data.csv` - CSV with columns: Merchant_Id, Merchant_Transaction_Id, Payment_Transaction_Id

4. **Output Files**: All script results will be automatically saved in the `output/` directory

## Scripts

### accounting_reversal_anomaly.py
Processes transaction IDs and checks for reversal anomalies using either Refund Orchestrator or Hermes APIs.

**Usage**: Run the script and choose between 'hermes' or 'ro' service when prompted.

### accounting_subscription.py
Checks mandate registration status for OMA IDs using the Hermes API.

**Usage**: Run the script and provide the input file name when prompted.

### forward_anomaly_v1.py & payments_transactions_v1.py
Process CSV data with merchant and payment information, making calls to both Hermes and Payment Service APIs.

**Usage**: Run the script with input_data.csv in the assets folder.

### split_large_files.py
Utility to split large CSV files into smaller chunks for processing.

**Usage**: Modify the source file path and run the script.

## Configuration

All configuration is now centralized:

- **URLs and Endpoints**: Defined in `constants.py`
- **Environment Variables**: Loaded from `.env` file via `utils.py`
- **Network Settings**: Proxy, timeouts, worker counts configurable via environment

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AUTHORIZATION_TOKEN` | JWT token for API authentication | Required |
| `PROXY_HOST` | SOCKS proxy hostname | localhost |
| `PROXY_PORT` | SOCKS proxy port | 1080 |
| `MAX_WORKERS` | Number of concurrent workers | 80 |
| `REQUEST_TIMEOUT` | HTTP request timeout in seconds | 15 |

## Security

- Authorization tokens are no longer hardcoded in scripts
- Use environment variables or .env files for sensitive configuration
- The .env file should never be committed to version control

## File Organization

- **Python scripts**: Keep in the main directory
- **Input data files**: Organized in the `assets/` directory
- **Output/result files**: Generated in the `output/` directory
- **Configuration**: Centralized in `constants.py` and `utils.py`
- **Credentials**: Stored in `.env` file (not committed to git)