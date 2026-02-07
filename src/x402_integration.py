"""
BookkeeperFinder API - x402 v2 on Base Mainnet
Custom middleware with Bazaar-compatible metadata.
"""

import base64
import json
import os
import sys
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware

# --- Config ---
WALLET_ADDRESS = os.getenv(
    "BASE_WALLET_ADDRESS",
    "0xb3e17988e6eE4D31e6D07decf363f736461d9e08",
)
NETWORK = "eip155:8453"
USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
AMOUNT = "100000"
MAX_TIMEOUT = 300

PROTECTED_ROUTES = {"/api/search", "/find"}

PAYMENT_REQUIRED_BODY = {
    "x402Version": 2,
    "error": "Payment required",
    "resource": {
        "url": "https://lexical-kalinda-x402-agents-10e84d5e.koyeb.app/api/search",
        "description": "Find verified bookkeepers and accountants",
        "mimeType": "application/json",
    },
    "accepts": [
        {
            "scheme": "exact",
            "network": NETWORK,
            "asset": USDC_ADDRESS,
            "amount": AMOUNT,
            "payTo": WALLET_ADDRESS,
            "maxTimeoutSeconds": MAX_TIMEOUT,
            "extra": {"name": "USDC", "version": "2"},
        }
    ],
    "extensions": {
        "bazaar": {
            "info": {
                "input": {
                    "specialty": "bookkeeper",
                    "location": "Miami, FL",
                    "method": "POST",
                },
                "output": {
                    "type": "json",
                    "example": {
                        "results": [
                            {
                                "name": "Example Bookkeeper",
                                "license_number": "BK123",
                                "rating": 4.8,
                                "verified": True,
                            }
                        ],
                        "count": 1,
                    },
                },
            },
        },
    },
}


class X402PaymentMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path not in PROTECTED_ROUTES or request.method != "POST":
            return await call_next(request)

        payment_header = (
            request.headers.get("X-PAYMENT")
            or request.headers.get("PAYMENT-SIGNATURE")
            or request.headers.get("x-payment")
        )

        if not payment_header:
            body_json = json.dumps(PAYMENT_REQUIRED_BODY)
            encoded = base64.b64encode(body_json.encode()).decode()
            return JSONResponse(
                status_code=402,
                content=PAYMENT_REQUIRED_BODY,
                headers={"PAYMENT-REQUIRED": encoded},
            )

        try:
            payload = json.loads(base64.b64decode(payment_header))
            if isinstance(payload, dict) and (
                "payload" in payload or "authorization" in payload
            ):
                response = await call_next(request)
                return response
        except Exception:
            pass

        return JSONResponse(
            status_code=402,
            content={"error": "Invalid payment signature"},
        )


app = FastAPI(title="BookkeeperFinder API", version="3.1.0")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.agent import agent

app.add_middleware(X402PaymentMiddleware)


class FindRequest(BaseModel):
    trade: str = "bookkeeper"
    service: str = "bookkeeper"
    location: str = "Miami, FL"
    min_rating: float = 4.0


@app.get("/")
async def root():
    return {
        "name": "BookkeeperFinder API",
        "version": "3.1.0",
        "price": "$0.10 USDC per call",
        "network": f"Base Mainnet ({NETWORK})",
        "wallet": WALLET_ADDRESS,
        "x402": {"version": 2, "bazaar": True},
        "endpoints": {
            "health": "/health",
            "find": "POST /find",
            "search": "POST /api/search",
        },
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "agent": "bookkeeper-finder",
        "version": "3.1.0",
        "payment_required": True,
        "price": "0.10 USDC",
        "network": NETWORK,
    }


@app.post("/find")
@app.post("/api/search")
async def find_bookkeepers_endpoint(body: FindRequest) -> dict[str, Any]:
    service = body.trade or body.service or "bookkeeper"
    result = agent.find_bookkeepers(
        service=service,
        location=body.location,
        min_rating=body.min_rating,
    )
    result["payment_status"] = "received"
    result["payment_amount"] = "0.10 USDC"
    result["payment_network"] = NETWORK
    return result


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
