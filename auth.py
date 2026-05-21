"""Простая аутентификация по API ключам"""
import json
import os
from config import API_KEYS_FILE

# Дефолтные ключи для старта
_DEFAULT_KEYS = {
    "demo": {"tier": "free", "daily_usage": 0},
}

def _load_keys() -> dict:
    if os.path.exists(API_KEYS_FILE):
        with open(API_KEYS_FILE) as f:
            return json.load(f)
    return dict(_DEFAULT_KEYS)

def _save_keys(keys: dict):
    with open(API_KEYS_FILE, "w") as f:
        json.dump(keys, f, indent=2)

def validate_key(api_key: str) -> dict:
    keys = _load_keys()
    if api_key in keys:
        return {"valid": True, "tier": keys[api_key]["tier"]}
    return {"valid": False, "tier": None}
