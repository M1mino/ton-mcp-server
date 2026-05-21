#!/usr/bin/env python3
"""TON Data MCP Server — ручная реализация на MCP SDK + Starlette SSE"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent
from ton_client import (
    get_wallet_balance,
    get_masterchain_info,
    get_stonfi_assets,
    get_token_price,
    get_market_overview,
)
from config import HOST, PORT
import anyio
import json

# Создаём MCP Server (низкоуровневый SDK)
server = Server("ton-data-mcp")

# ─── Определяем инструменты ──────────────────────────────────

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_balance",
            description="Баланс TON кошелька по адресу. Адрес начинается с EQ или UQ.",
            inputSchema={
                "type": "object",
                "properties": {
                    "address": {"type": "string", "description": "Адрес TON кошелька (EQ... или UQ...)"}
                },
                "required": ["address"],
            },
        ),
        Tool(
            name="get_token_price",
            description="Цена токена на STON.fi. Для TON используй стандартный адрес.",
            inputSchema={
                "type": "object",
                "properties": {
                    "token_address": {"type": "string", "description": "Адрес токена (контракта)"}
                },
                "required": ["token_address"],
            },
        ),
        Tool(
            name="get_market_overview",
            description="Обзор рынка TON: текущий блок, цена TON к USDT через STON.fi пул.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="search_tokens",
            description="Поиск токенов на STON.fi по названию или символу.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Название или символ токена"},
                    "limit": {"type": "integer", "description": "Максимум результатов", "default": 5},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_blockchain_info",
            description="Текущее состояние блокчейна TON: номер блока, шард, воркчейн.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "get_balance":
        addr = arguments["address"]
        result = get_wallet_balance(addr)
        if "error" in result:
            return [TextContent(type="text", text=f"❌ {result['error']}")]
        return [TextContent(type="text", text=(
            f"**Адрес:** `{result['address'][:15]}...`\n"
            f"**Баланс:** {result['balance_ton']:.4f} TON\n"
            f"**Тип:** {result['wallet_type']}\n"
            f"**Статус:** {result['account_state']}"
        ))]
    
    elif name == "get_token_price":
        addr = arguments["token_address"]
        result = get_token_price(addr)
        if "error" in result:
            return [TextContent(type="text", text=f"❌ {result['error']}")]
        return [TextContent(type="text", text=(
            f"**Цена:** {result['price']:.10f} TON\n"
            f"**Пул:** `{result['pool_address'][:20]}...`\n"
            f"**Резерв token0:** {result['reserve0']:.2f}\n"
            f"**Резерв token1:** {result['reserve1']:.2f}"
        ))]
    
    elif name == "get_market_overview":
        result = get_market_overview()
        bc = result.get("blockchain", {})
        price = result.get("ton_price_usdt", "N/A")
        return [TextContent(type="text", text=(
            f"**Блокчейн TON**\n"
            f"• Последний блок: {bc.get('seqno', 'N/A')}\n\n"
            f"**Рынок**\n"
            f"• Цена TON: {price}\n"
            f"• Источник: STON.fi TON/USDT пул"
        ))]
    
    elif name == "search_tokens":
        query = arguments.get("query", "")
        limit = min(arguments.get("limit", 5), 20)
        assets = get_stonfi_assets(query, limit)
        if not assets:
            return [TextContent(type="text", text="Токены не найдены")]
        if "error" in assets[0]:
            return [TextContent(type="text", text=f"❌ {assets[0]['error']}")]
        lines = [f"**Найдено токенов:** {len(assets)}"]
        for a in assets:
            lines.append(f"• **{a['symbol']}** — {a['name']}")
        return [TextContent(type="text", text="\n".join(lines))]
    
    elif name == "get_blockchain_info":
        info = get_masterchain_info()
        if "error" in info:
            return [TextContent(type="text", text=f"❌ {info['error']}")]
        return [TextContent(type="text", text=(
            f"**Masterchain**\n"
            f"• Высота: {info['seqno']:,}\n"
            f"• Шард: {info['shard']}\n"
            f"• Воркчейн: {info['workchain']}"
        ))]
    
    raise ValueError(f"Unknown tool: {name}")


# ─── Запуск через SSE ────────────────────────────────────────

def main():
    from mcp.server.sse import SseServerTransport
    from starlette.applications import Starlette
    from starlette.routing import Mount, Route
    from starlette.middleware.cors import CORSMiddleware
    import uvicorn
    
    sse = SseServerTransport("/messages/")
    
    async def handle_sse(request):
        async with anyio.create_task_group() as tg:
            await sse.handle_sse(request, server.create_initialization_options(), tg)
    
    async def handle_messages(request):
        await sse.handle_post_message(request, server.create_initialization_options())
    
    starlette_app = Starlette(
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", routes=[
                Route("/", endpoint=handle_messages, methods=["POST"]),
            ]),
        ],
    )
    
    # CORS middleware добавляем отдельно
    from starlette.middleware import Middleware
    starlette_app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
    
    print(f"🚀 TON Data MCP Server запущен на {HOST}:{PORT}")
    print(f"📡 SSE: http://{HOST}:{PORT}/sse")
    print(f"📬 Messages: http://{HOST}:{PORT}/messages/")
    print(f"🔑 Demo key: demo")
    print(f"📋 Инструменты: get_balance, get_token_price, get_market_overview, search_tokens, get_blockchain_info")
    
    uvicorn.run(starlette_app, host=HOST, port=PORT, log_level="info")

if __name__ == "__main__":
    main()
