FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir "x402[fastapi,evm]>=2.0.0"

# Copy source code
COPY src/ ./src/
COPY automation/ ./automation/
# Note: .env is not copied - use Railway environment variables instead

# Expose port
EXPOSE 8000

# Run the x402 integration server
CMD ["sh", "-c", "python -m uvicorn src.x402_integration:app --host 0.0.0.0 --port ${PORT:-8000}"]
