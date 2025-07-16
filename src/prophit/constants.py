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

# Color Scheme (Flat UI Colors)
COLORS = {
    "PRIMARY": "#3742fa",        # Blue
    "SECONDARY": "#2ed573",      # Green (Yes)
    "DANGER": "#ff3838",         # Red (No)
    "BACKGROUND": "#f1f2f6",     # Light gray
    "SURFACE": "#ffffff",        # White
    "TEXT": "#2f3542",          # Dark gray
    "TEXT_LIGHT": "#747d8c",    # Medium gray
    "BORDER": "#dfe4ea",        # Light border
    "ACCENT": "#ffa502",        # Orange accent
    "PURPLE": "#5352ed",        # Purple
    "TURQUOISE": "#7bed9f",     # Light green
    "YELLOW": "#ffc048"         # Yellow
}

# Database Defaults
DEFAULT_MARKET_TYPE = MARKET_TYPES["BINARY"]
DEFAULT_MARKET_STATUS = MARKET_STATUSES["ACTIVE"]