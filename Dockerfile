FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY automation/ ./automation/
# Note: .env is not copied - use Railway environment variables instead

# Expose port
EXPOSE 8000

# Run the x402 integration server
CMD ["python", "-m", "uvicorn", "src.x402_integration:app", "--host", "0.0.0.0", "--port", "8000"]
