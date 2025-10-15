"""
Utility functions for PhonePe API scripts.
Handles environment loading, common configurations, and shared functionality.
"""

import os
import warnings
import urllib3
import socks
import socket
from constants import NETWORK_CONFIG, API_BASE_URLS, API_ENDPOINTS, EVENT_TYPES, QUERY_PARAMS, DEFAULT_PATHS

def load_env():
    """
    Load environment variables from .env file if it exists.
    """
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

def get_auth_token():
    """
    Get the authorization token from environment variables.
    """
    load_env()
    token = os.getenv('AUTHORIZATION_TOKEN')
    if not token:
        raise ValueError(
            "AUTHORIZATION_TOKEN not found in environment. "
            "Please set it in your .env file or environment variables."
        )
    return f"{token}"

def get_headers():
    """
    Get the standard headers with authorization token.
    """
    return {
        'Authorization': get_auth_token()
    }

def setup_proxy():
    """
    Configure SOCKS proxy for all socket traffic.
    """
    try:
        proxy_host = os.getenv('PROXY_HOST', NETWORK_CONFIG['proxy']['host'])
        proxy_port = int(os.getenv('PROXY_PORT', NETWORK_CONFIG['proxy']['port']))
        
        socks.set_default_proxy(socks.SOCKS5, proxy_host, proxy_port)
        socket.socket = socks.socksocket
        print(f"SOCKS5 proxy configured successfully ({proxy_host}:{proxy_port}).")
        return True
    except socks.ProxyError as e:
        print(f"Error: Could not configure SOCKS proxy. Is the proxy server running? {e}")
        return False

def disable_ssl_warnings():
    """
    Disable SSL warnings for unverified HTTPS requests.
    """
    warnings.filterwarnings('ignore', category=urllib3.exceptions.InsecureRequestWarning)

def get_network_config():
    """
    Get network configuration with environment overrides.
    """
    return {
        'max_workers': int(os.getenv('MAX_WORKERS', NETWORK_CONFIG['max_workers'])),
        'timeout': int(os.getenv('REQUEST_TIMEOUT', NETWORK_CONFIG['request_timeout']))
    }

def build_api_url(service, endpoint, event_type=None, query_params=None):
    """
    Build a complete API URL from components.
    
    Args:
        service: Service name (e.g., 'hermes', 'refund_orchestrator')
        endpoint: Endpoint name (e.g., 'accounting_event_details')
        event_type: Optional event type (e.g., 'merchant_fulfilment_reversal')
        query_params: Optional query parameters (e.g., 'already_reversed_fetch_limit')
    
    Returns:
        Complete URL string
    """
    base_url = API_BASE_URLS[service]
    endpoint_path = API_ENDPOINTS[service][endpoint]
    
    url = f"{base_url}{endpoint_path}"
    
    if event_type:
        url += EVENT_TYPES[event_type]
    
    if query_params:
        url += QUERY_PARAMS[query_params]
    
    return url

def ensure_output_dir():
    """
    Ensure the output directory exists.
    """
    output_dir = DEFAULT_PATHS['output_dir']
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

def show_available_assets(file_extensions=None):
    """
    Display available files in the assets directory.
    
    Args:
        file_extensions: List of file extensions to filter by (e.g., ['.csv', '.txt'])
                        If None, shows all files
    """
    assets_dir = DEFAULT_PATHS['assets_dir']
    print(f"Available files in {assets_dir} directory:")
    
    if not os.path.exists(assets_dir):
        print(f"  - {assets_dir} directory not found!")
        return []
    
    files = []
    for file in os.listdir(assets_dir):
        # Skip hidden files and directories
        if file.startswith('.'):
            continue
        
        file_path = os.path.join(assets_dir, file)
        if os.path.isfile(file_path):
            # Filter by extensions if provided
            if file_extensions is None or any(file.endswith(ext) for ext in file_extensions):
                files.append(file)
                print(f"  - {file}")
    
    if not files:
        if file_extensions:
            extensions_str = ", ".join(file_extensions)
            print(f"  - No files with extensions {extensions_str} found!")
        else:
            print(f"  - No files found!")
    
    return files

def get_asset_file_path(filename):
    """
    Get the full relative path to an asset file.
    
    Args:
        filename: Name of the file in the assets directory
    
    Returns:
        Relative path to the file
    """
    if '/' in filename:
        # If already a path, return as-is
        return filename
    else:
        # If just a filename, prepend assets directory
        return f"{DEFAULT_PATHS['assets_dir']}/{filename}"

def get_api_config():
    """
    Get the API configuration dictionary for backward compatibility.
    """
    return {
        "ro": {
            "base_url": build_api_url('refund_orchestrator', 'accounting_events'),
            "endpoint_suffix": EVENT_TYPES['merchant_fulfilment_reversal']
        },
        "hermes": {
            "base_url": build_api_url('hermes', 'accounting_event_details'),
            "endpoint_suffix": EVENT_TYPES['merchant_fulfilment_reversal']
        },
        "mandate_check": {
            "base_url": build_api_url('hermes', 'accounting_event_details'),
            "endpoint_suffix": EVENT_TYPES['merchant_mandate_registration']
        },
        "payments_debug": {
            "base_url": build_api_url('payment_service', 'housekeeping_debug'),
            "endpoint_suffix": QUERY_PARAMS['already_reversed_fetch_limit']
        },
        "hermes_status_check": {
            "base_url": build_api_url('hermes', 'db_status_check'),
            "endpoint_suffix": ""
        }
    }