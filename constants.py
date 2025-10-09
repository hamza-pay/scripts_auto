"""
Constants and configuration for PhonePe API scripts.
Contains all URLs, endpoints, and configuration values.
"""

# ================================================================
# API BASE URLS
# ================================================================

API_BASE_URLS = {
    "hermes": "https://hermes.drove.mer.phonepe.mhx",
    "refund_orchestrator": "https://refund-orchestrator.drove.mer.phonepe.mhx",
    "payment_service": "https://paymentservice-txnl.drove.pymts.phonepe.nm5"
}

# ================================================================
# API ENDPOINTS
# ================================================================

API_ENDPOINTS = {
    "hermes": {
        "accounting_event_details": "/v1/housekeeping/accountingEventDetails",
        "db_status_check": "/v1/housekeeping/db"
    },
    "refund_orchestrator": {
        "accounting_events": "/v1/accounting/events"
    },
    "payment_service": {
        "housekeeping_debug": "/v1/housekeeping/debug"
    }
}

# ================================================================
# EVENT TYPES
# ================================================================

EVENT_TYPES = {
    "merchant_fulfilment_reversal": "/MERCHANT_FULFILMENT_REVERSAL",
    "merchant_mandate_registration": "/MERCHANT_MANDATE_REGISTRATION"
}

# ================================================================
# QUERY PARAMETERS
# ================================================================

QUERY_PARAMS = {
    "already_reversed_fetch_limit": "?alreadyReversedFetchLimit=1000"
}

# ================================================================
# NETWORK CONFIGURATION
# ================================================================

NETWORK_CONFIG = {
    "max_workers": 80,
    "request_timeout": 15,
    "proxy": {
        "type": "SOCKS5",
        "host": "localhost",
        "port": 1080
    }
}

# ================================================================
# FILE PATHS
# ================================================================

DEFAULT_PATHS = {
    "assets_dir": "assets",
    "output_dir": "output",
    "input_transactions": "assets/input_transactions.txt",
    "input_data": "assets/input_data.csv",
    "output_responses": "output/api_responses.csv"
}

# ================================================================
# API RESPONSE KEYS
# ================================================================

RESPONSE_KEYS = {
    "reconciliation_state": "reconciliationState",
    "execution_state": "executionState",
    "message": "message",
    "data": "data"
}

# ================================================================
# DEFAULT VALUES
# ================================================================

DEFAULTS = {
    "reconciliation_state_not_found": "RECON_STATE_NOT_FOUND",
    "execution_state_not_found": "EXEC_STATE_NOT_FOUND",
    "message_not_found": "MESSAGE_NOT_FOUND",
    "no_response": "NO RESPONSE",
    "json_decode_error": "Error decoding JSON",
    "unknown_service": "Unknown Service",
    "skipped": "SKIPPED",
    "not_available": "N/A"
}