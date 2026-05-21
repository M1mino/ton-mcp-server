"""TON Data MCP Server — Configuration"""
import os

# Сервер
HOST = os.getenv("MCP_HOST", "0.0.0.0")
PORT = int(os.getenv("MCP_PORT", "8001"))

# TON API
TONCENTER_BASE = "https://toncenter.com/api/v2"
STONFI_BASE = "https://api.ston.fi/v1"

# Rate limits (free tier)
FREE_DAILY_LIMIT = 100
FREE_RATE_PER_MINUTE = 10

# Pro tier (будущее)
PRO_DAILY_LIMIT = 10000
PRO_RATE_PER_MINUTE = 100

# API keys storage (simple file-based for now)
API_KEYS_FILE = os.path.join(os.path.dirname(__file__), "api_keys.json")
