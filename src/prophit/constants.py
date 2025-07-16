# Database Configuration
DATABASE_URL = "sqlite:///prophit.db"

# LMSR Configuration
DEFAULT_LIQUIDITY_PARAM = 100.0
MIN_LIQUIDITY_PARAM = 10.0
MAX_LIQUIDITY_PARAM = 1000.0

# Market Configuration
MARKET_TYPES = {
    "BINARY": "binary",
    "CATEGORICAL": "categorical", 
    "NUMERICAL": "numerical"
}

MARKET_STATUSES = {
    "ACTIVE": "active",
    "CLOSED": "closed",
    "RESOLVED": "resolved"
}

# Trading Configuration
MIN_TRADE_QUANTITY = 1.0
MAX_TRADE_QUANTITY = 10000.0
DEFAULT_TRADE_QUANTITY = 10.0

# Binary Market Outcomes
BINARY_OUTCOMES = {
    "NO": 0,
    "YES": 1
}

# User Configuration
DEFAULT_USER_ID = "user123"  # TODO: Replace with actual authentication

# UI Configuration
MAX_MARKETS_PER_PAGE = 50
MARKET_CARD_REFRESH_INTERVAL = 5000  # milliseconds

# Color Scheme (CSS Variables)
COLORS = {
    "PRIMARY": "#6366f1",
    "PRIMARY_LIGHT": "#8b5cf6", 
    "SECONDARY": "#10b981",
    "DANGER": "#ef4444",
    "SURFACE": "#ffffff",
    "SURFACE_2": "#f8fafc",
    "SURFACE_3": "#f1f5f9",
    "TEXT": "#1e293b",
    "TEXT_LIGHT": "#64748b",
    "BORDER": "#e2e8f0",
    "BORDER_LIGHT": "#f1f5f9"
}

# Database Defaults
DEFAULT_MARKET_TYPE = MARKET_TYPES["BINARY"]
DEFAULT_MARKET_STATUS = MARKET_STATUSES["ACTIVE"]