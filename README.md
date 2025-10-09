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
├── filter_mids.py                  # CSV filtering script for merchant IDs
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

3. **Input Files**: Place your input files in the `assets/` directory. The scripts will automatically detect and display available files for selection:
   - `.txt` files for transaction ID lists (one ID per line)
   - `.csv` files for structured data with columns like Merchant_Id, Merchant_Transaction_Id, Payment_Transaction_Id

4. **Interactive File Selection**: All scripts now provide an interactive interface that:
   - Shows available files in the assets directory
   - Filters files by appropriate extensions (.csv or .txt)
   - Prompts you to select the file you want to process

5. **Output Files**: All script results will be automatically saved in the `output/` directory

## Scripts

### accounting_reversal_anomaly.py
Processes transaction IDs and checks for reversal anomalies using either Refund Orchestrator or Hermes APIs.

**Features**:
- Interactive file selection from available .txt files in assets directory
- Service selection between 'hermes' and 'ro'
- Concurrent processing with configurable worker count

**Usage**: Run the script, select your input file, and choose the service when prompted.

### accounting_subscription.py
Checks mandate registration status for OMA IDs using the Hermes API.

**Features**:
- Interactive file selection from available .txt files
- Concurrent API processing
- Detailed reconciliation state reporting

**Usage**: Run the script and select the input file containing OMA IDs.

### forward_anomaly_v1.py & payments_transactions_v1.py
Process CSV data with merchant and payment information, making calls to both Hermes and Payment Service APIs.

**Features**:
- Interactive CSV file selection from assets directory
- Dual API processing (Hermes + Payment Service)
- Comprehensive error handling and response parsing

**Usage**: Run the script and select your CSV file when prompted.

### filter_mids.py
Filters large CSV files by merchant ID with chunked processing for memory efficiency.

**Features**:
- Interactive CSV file selection
- Custom output filename specification
- Memory-efficient chunked processing
- Configurable filter criteria

**Usage**: Run the script, select your CSV file, specify output filename, and the script will filter data and save to the output directory.

### split_large_files.py
Utility to split large CSV files into smaller chunks for processing.

**Features**:
- Interactive CSV file selection
- Configurable chunk size (default: 500,000 rows)
- Automatic output file naming

**Usage**: Run the script and select the large CSV file you want to split.

## Configuration

All configuration is now centralized and uses relative paths:

- **URLs and Endpoints**: Defined in `constants.py`
- **Environment Variables**: Loaded from `.env` file via `utils.py`
- **Network Settings**: Proxy, timeouts, worker counts configurable via environment
- **File Paths**: All paths are relative, making the scripts portable across different environments
- **Interactive Features**: New utility functions in `utils.py` provide file discovery and user-friendly interfaces

## Key Features

### Improved User Experience
- **Interactive File Selection**: All scripts automatically detect and display available files
- **File Type Filtering**: Scripts show only relevant file types (.csv for data processing, .txt for transaction lists)
- **Clear Instructions**: Each script provides helpful prompts and displays available options
- **Portable Paths**: No hardcoded absolute paths - scripts work from any location

### Enhanced Functionality
- **Memory Efficient**: Large file processing uses chunked reading to minimize memory usage
- **Concurrent Processing**: Configurable multi-threading for API calls
- **Error Handling**: Comprehensive error handling with informative messages
- **Flexible Output**: Customizable output filenames and automatic directory creation

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
- **Input data files**: Organized in the `assets/` directory (automatically detected by scripts)
- **Output/result files**: Generated in the `output/` directory (automatically created if needed)
- **Configuration**: Centralized in `constants.py` and `utils.py`
- **Credentials**: Stored in `.env` file (not committed to git)

## Getting Started

1. Clone or download the scripts to your local machine
2. Set up your environment file with API credentials
3. Place your data files in the `assets/` directory
4. Run any script - it will guide you through the process:
   ```bash
   python3 filter_mids.py
   ```
5. Follow the interactive prompts to select files and configure options
6. Results will be saved automatically in the `output/` directory

The scripts are designed to be user-friendly and will show you exactly what files are available and what options you have at each step.