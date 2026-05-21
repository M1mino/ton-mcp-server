FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Код
COPY server.py config.py ton_client.py auth.py rate_limiter.py ./
COPY .well-known ./.well-known/

# Порт HF Space
ENV MCP_PORT=7860

# Запуск
CMD ["python", "server.py"]
