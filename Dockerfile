FROM python:3.12-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends     git     && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY server.py config.py ton_client.py auth.py rate_limiter.py x402_mcp.py ./
COPY .well-known ./.well-known/

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3     CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/health')" 2>/dev/null || exit 1

# Port
EXPOSE 8001

# Start
CMD ["python", "server.py"]
