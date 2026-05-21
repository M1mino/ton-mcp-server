# TON Data MCP Server 🚀

> MCP-сервер для данных блокчейна TON: балансы кошельков, цены токенов, пулы ликвидности STON.fi, обзор рынка.

Подключается к любому AI-агенту, поддерживающему [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) — Claude, Cursor, Hermes Agent, OpenClaw и другие.

## Быстрый старт

### Через MCP клиент

```json
{
  "mcpServers": {
    "ton-data": {
      "url": "http://81.177.159.90:8001/mcp",
      "headers": {
        "X-API-Key": "demo"
      }
    }
  }
}
```

### Через CLI

```bash
# Установка
pip install mcp

# Подключение
mcp run http://81.177.159.90:8001
```

## Инструменты

| Инструмент | Описание | Бесплатно |
|-----------|----------|-----------|
| `get_balance` | Баланс TON кошелька по адресу | ✅ 100 запр/день |
| `get_token_price` | Цена токена на STON.fi | ✅ |
| `get_market_overview` | Обзор рынка TON (блок, цена) | ✅ |
| `search_tokens` | Поиск токенов на STON.fi | ✅ |
| `get_transactions` | Последние транзакции адреса | ✅ |
| `get_blockchain_info` | Состояние блокчейна TON | ✅ |

## Архитектура

```
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│  AI-агент    │────▶│  MCP-сервер  │────▶│  Toncenter API   │
│  (Claude/    │◀────│  (FastMCP)   │◀────│  + STON.fi API   │
│  Hermes/     │     │  :8001       │     │                  │
│  OpenClaw)   │     │              │     │                  │
└──────────────┘     └──────────────┘     └──────────────────┘
```

## Разработка

```bash
# Клонировать
git clone https://github.com/your-org/ton-mcp-server
cd ton-mcp-server

# Зависимости
pip install mcp fastmcp uvicorn httpx

# Запуск
python server.py
```

## API ключи

**Free tier:** `demo` — 100 запросов/день, 10 запр/мин

Pro tier (скоро): от $5/мес — безлимит, приоритет

## Публикация

- [Smithery.ai](https://smithery.ai) — скоро
- [Awesome MCP Servers](https://github.com/punkpeye/awesome-mcp-servers) — PR отправлен

## Лицензия

MIT
