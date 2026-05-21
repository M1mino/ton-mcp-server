#!/usr/bin/env python3
"""TON Data MCP Server — предоставляет TON блокчейн данные другим AI-агентам.

Запуск: python3 server.py
Или через MCP: mcp run server.py
"""

import sys
import os
from typing import Optional

# Добавляем путь к модулям
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server.fastmcp import FastMCP
from ton_client import (
    get_wallet_balance,
    get_masterchain_info,
    get_transactions,
    get_stonfi_assets,
    get_token_price,
    get_market_overview,
)
from config import HOST, PORT

# Создаём MCP сервер
mcp = FastMCP(
    "TON Data MCP",
    instructions="Данные блокчейна TON: балансы кошельков, цены токенов, пулы ликвидности, обзор рынка",
    host=HOST,
    port=PORT,
    sse_path="/sse",
    streamable_http_path="/mcp",
    mount_path="/",
)

# ─── Инструменты ───────────────────────────────────────────────

@mcp.tool(
    name="get_balance",
    description="Получить баланс TON кошелька по адресу. Адрес начинается с EQ или UQ."
)
def get_balance(address: str) -> str:
    """Баланс кошелька TON"""
    result = get_wallet_balance(address)
    if "error" in result:
        return f"❌ {result['error']}"
    
    return (
        f"**Адрес:** `{result['address'][:15]}...`\n"
        f"**Баланс:** {result['balance_ton']:.4f} TON\n"
        f"**Тип кошелька:** {result['wallet_type']}\n"
        f"**Статус:** {result['account_state']}"
    )


@mcp.tool(
    name="get_token_price",
    description="Получить цену токена на STON.fi по его контракту. Для TON используй адрес EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c"
)
def get_token_price_tool(token_address: str) -> str:
    """Цена токена через пулы STON.fi"""
    result = get_token_price(token_address)
    if "error" in result:
        return f"❌ {result['error']}"
    
    return (
        f"**Цена:** {result['price']:.10f} TON\n"
        f"**Пул:** `{result['pool_address'][:20]}...`\n"
        f"**Резерв token0:** {result['reserve0']:.2f}\n"
        f"**Резерв token1:** {result['reserve1']:.2f}"
    )


@mcp.tool(
    name="get_market_overview",
    description="Обзор рынка TON: текущий блок блокчейна, цена TON к USDT"
)
def get_market_overview_tool() -> str:
    """Обзор рынка TON"""
    result = get_market_overview()
    
    bc = result.get("blockchain", {})
    price = result.get("ton_price_usdt", "N/A")
    
    if price != "N/A":
        price_str = f"${float(price) * 2:.2f} (примерно, через TON/USDT пул)"
    else:
        price_str = "N/A"
    
    return (
        f"**Блокчейн TON**\n"
        f"• Последний блок: {bc.get('seqno', 'N/A')}\n"
        f"• Шард: {bc.get('shard', 'N/A')}\n\n"
        f"**Рынок**\n"
        f"• Цена TON: {price_str}\n"
        f"• Источник: STON.fi TON/USDT пул"
    )


@mcp.tool(
    name="search_tokens",
    description="Поиск токенов на STON.fi по названию или символу"
)
def search_tokens(query: str, limit: int = 5) -> str:
    """Поиск токенов"""
    assets = get_stonfi_assets(query, min(limit, 20))
    
    if not assets:
        return "Токены не найдены"
    if "error" in assets[0]:
        return f"❌ {assets[0]['error']}"
    
    lines = [f"**Найдено токенов:** {len(assets)}"]
    for a in assets:
        lines.append(f"• **{a['symbol']}** — {a['name']}")
    
    return "\n".join(lines)


@mcp.tool(
    name="get_transactions",
    description="Последние транзакции TON кошелька"
)
def get_transactions_tool(address: str, limit: int = 5) -> str:
    """Транзакции адреса"""
    txs = get_transactions(address, min(limit, 20))
    
    if not txs:
        return "Транзакции не найдены"
    
    lines = [f"**Последние {len(txs)} транзакций:**"]
    for tx in txs:
        if "error" in tx:
            lines.append(f"❌ {tx['error']}")
        else:
            lines.append(f"• LT: `{tx['lt']}` | Hash: `{tx['hash']}...`")
    
    return "\n".join(lines)


@mcp.tool(
    name="get_blockchain_info",
    description="Текущее состояние блокчейна TON (номер блока, шард)"
)
def get_blockchain_info() -> str:
    """Информация о блокчейне"""
    info = get_masterchain_info()
    if "error" in info:
        return f"❌ {info['error']}"
    
    return (
        f"**Masterchain**\n"
        f"• Высота: {info['seqno']:,}\n"
        f"• Шард: {info['shard']}\n"
        f"• Воркчейн: {info['workchain']}"
    )


# ─── Запуск ────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    
    print(f"🚀 TON Data MCP Server запущен на {HOST}:{PORT}")
    print(f"📡 SSE endpoint: http://{HOST}:{PORT}/sse")
    print(f"📬 Messages endpoint: http://{HOST}:{PORT}/messages/")
    print(f"🔑 Demo API key: demo (free tier: {100} запросов/день)")
    print(f"📋 Инструменты: get_balance, get_token_price, get_market_overview, search_tokens, get_transactions, get_blockchain_info")
    
    starlette_app = mcp.sse_app()
    uvicorn.run(starlette_app, host=HOST, port=PORT, log_level="info")
