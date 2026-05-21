---
title: TON Data MCP Server
emoji: 🚀
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
---

# TON Data MCP Server

MCP-сервер для данных блокчейна TON: балансы кошельков, цены токенов, пулы ликвидности STON.fi, обзор рынка.

Подключается к любому AI-агенту, поддерживающему MCP.

## Использование

```json
{
  "mcpServers": {
    "ton-data": {
      "url": "https://Som919-ton-mcp-server.hf.space/mcp",
      "headers": { "X-API-Key": "demo" }
    }
  }
}
```

## Инструменты

- `get_balance` — баланс TON кошелька
- `get_token_price` — цена токена на STON.fi
- `get_market_overview` — обзор рынка TON
- `search_tokens` — поиск токенов
- `get_transactions` — последние транзакции
- `get_blockchain_info` — состояние блокчейна
