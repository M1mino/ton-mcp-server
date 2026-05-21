"""TON API Client — запросы к Toncenter и STON.fi"""
import json
import urllib.request
import time
from typing import Optional

from config import TONCENTER_BASE, STONFI_BASE

# Простой rate limiter — не чаще 1 запроса в секунду
_last_request_time = 0

def _rate_limited_request(url: str, timeout: int = 15) -> dict:
    global _last_request_time
    now = time.time()
    if now - _last_request_time < 1.0:
        time.sleep(1.0 - (now - _last_request_time))
    _last_request_time = time.time()
    
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)

def get_wallet_balance(address: str) -> dict:
    """Баланс TON кошелька"""
    try:
        data = _rate_limited_request(
            f"{TONCENTER_BASE}/getWalletInformation?address={address}"
        )
        if data.get("ok") and data.get("result", {}).get("wallet"):
            balance_nano = int(data["result"]["balance"])
            return {
                "address": address,
                "balance_ton": balance_nano / 1e9,
                "balance_nano": balance_nano,
                "wallet_type": data["result"].get("wallet_type", "unknown"),
                "seqno": data["result"].get("seqno", 0),
                "account_state": data["result"].get("account_state", "unknown"),
            }
        return {"error": "Wallet not found or inactive", "address": address}
    except Exception as e:
        return {"error": str(e), "address": address}

def get_masterchain_info() -> dict:
    """Текущий блок и состояние блокчейна"""
    try:
        data = _rate_limited_request(f"{TONCENTER_BASE}/getMasterchainInfo")
        if data.get("ok"):
            last = data["result"]["last"]
            return {
                "seqno": last["seqno"],
                "shard": last["shard"],
                "workchain": last["workchain"],
                "file_hash": last["file_hash"][:20],
            }
        return {"error": "Cannot get masterchain info"}
    except Exception as e:
        return {"error": str(e)}

def get_transactions(address: str, limit: int = 5) -> list:
    """Последние транзакции адреса"""
    try:
        data = _rate_limited_request(
            f"{TONCENTER_BASE}/getTransactions?address={address}&limit={limit}"
        )
        if data.get("ok"):
            txs = data.get("result", [])
            result = []
            for tx in txs[:limit]:
                result.append({
                    "lt": tx.get("transaction_id", {}).get("lt", ""),
                    "hash": str(tx.get("transaction_id", {}).get("hash", ""))[:20],
                    "fee": tx.get("fee", "0"),
                    "utime": tx.get("utime", ""),
                })
            return result
        return []
    except Exception as e:
        return [{"error": str(e)}]

def get_stonfi_assets(query: str = "", limit: int = 5) -> list:
    """Поиск токенов на STON.fi"""
    try:
        url = f"{STONFI_BASE}/assets?limit={limit}"
        if query:
            url += f"&search={query}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.load(resp)
        
        assets = data.get("asset_list", [])
        result = []
        for a in assets[:limit]:
            result.append({
                "symbol": a.get("symbol", "?"),
                "name": a.get("display_name", "?"),
                "address": a.get("contract_address", "?"),
                "decimals": a.get("decimals", 9),
            })
        return result
    except Exception as e:
        return [{"error": str(e)}]

def get_token_price(token_address: str) -> dict:
    """Цена токена (через STON.fi pools)"""
    try:
        req = urllib.request.Request(f"{STONFI_BASE}/pools")
        with urllib.request.urlopen(req, timeout=30) as resp:
            pools = json.load(resp).get("pool_list", [])
        
        # Ищем пул с этим токеном
        for p in pools:
            t0 = p.get("token0_address", "")
            t1 = p.get("token1_address", "")
            if token_address in (t0, t1):
                r0 = int(p.get("reserve0", "0")) / 1e9
                r1 = int(p.get("reserve1", "0")) / 1e9
                is_token0 = token_address == t0
                price = r1 / r0 if is_token0 else r0 / r1
                return {
                    "pool_address": p.get("address", "?"),
                    "price": round(price, 10),
                    "reserve0": r0,
                    "reserve1": r1,
                    "token0": t0[:20],
                    "token1": t1[:20],
                }
        return {"error": "Token not found in any pool"}
    except Exception as e:
        return {"error": str(e)}

def get_market_overview() -> dict:
    """Обзор рынка TON"""
    mcinfo = get_masterchain_info()
    # TON price from STON.fi (TON/USDT pool)
    ton_address = "EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c"
    usdt_address = "EQCxE6mUtQJKFnGfaROTKOt1lZbDiiX1kCixRv7Nw2Id_sDs"
    
    price_info = get_token_price(ton_address)
    
    return {
        "blockchain": mcinfo,
        "ton_price_usdt": price_info.get("price", "N/A"),
        "note": "Цена TON получена из пула TON/USDT на STON.fi",
    }
