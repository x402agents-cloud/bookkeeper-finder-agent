"""
BookkeeperFinder API - x402 Payment Integration
Simple x402 middleware (MVP mode) with Bazaar discovery metadata
"""

import os
import sys
import json
from typing import Any, Optional, Tuple

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# --- Config ---
WALLET_ADDRESS = os.getenv(
    "BASE_WALLET_ADDRESS",
    "0xb3e17988e6eE4D31e6D07decf363f736461d9e08",
)
FACILITATOR_URL = os.getenv("X402_FACILITATOR_URL", "https://x402.org/facilitator")

# --- FastAPI App ---
app = FastAPI(title="BookkeeperFinder API", version="2.0.0")


# --- Simple x402 Middleware ---
class x402Middleware:
    def __init__(self, price_usd: float = 0.10):
        self.price = price_usd
        self.asset = "USDC"
        self.network = "base"
        self.receiver = WALLET_ADDRESS
        self.facilitator = FACILITATOR_URL

    def check_payment(self, request_headers: dict) -> Tuple[bool, Optional[dict], str]:
        payment_header = (
            request_headers.get("x-payment-signature")
            or request_headers.get("X-Payment-Signature")
        )
        if not payment_header:
            return False, None, "Missing X-Payment-Signature header"
        try:
            payment_info = json.loads(payment_header)
        except json.JSONDecodeError:
            return False, None, "Invalid payment signature format"
        if not payment_info.get("tx_hash") and not payment_info.get("signature"):
            return False, None, "Payment missing transaction hash or signature"
        return True, payment_info, "Payment accepted (MVP mode)"

    def get_payment_required_response(self) -> dict:
        return {
            "error": "Payment Required",
            "status": 402,
            "payment": {
                "scheme": "exact",
                "network": self.network,
                "asset": self.asset,
                "amount": str(self.price),
                "receiver": self.receiver,
                "facilitator": self.facilitator,
                "memo": "BookkeeperFinder API call",
            },
        }


payment_middleware = x402Middleware()


# --- Import agent ---
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.agent import agent


class FindRequest(BaseModel):
    service: str = "bookkeeper"
    location: str = "Miami, FL"
    min_rating: float = 4.0


@app.middleware("http")
async def x402_payment_check(request: Request, call_next):
    if request.url.path in ["/health", "/", "/docs", "/openapi.json", "/payment-info"]:
        return await call_next(request)
    is_paid, payment_info, error_msg = payment_middleware.check_payment(dict(request.headers))
    if not is_paid:
        return JSONResponse(status_code=402, content=payment_middleware.get_payment_required_response())
    request.state.payment = payment_info
    return await call_next(request)


@app.get("/")
async def root():
    return {
        "name": "BookkeeperFinder API",
        "version": "2.0.0",
        "price": "$0.10 USDC per call",
        "network": "Base (eip155:8453)",
        "wallet": WALLET_ADDRESS,
        "endpoints": {
            "health": "/health",
            "find": "POST /find (requires $0.10 USDC payment)",
        },
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "agent": "bookkeeper-finder",
        "version": "2.0.0",
        "payment_required": True,
        "price": "0.10 USDC",
        "network": "eip155:8453",
    }


@app.post("/find")
async def find_bookkeepers_endpoint(body: FindRequest) -> dict[str, Any]:
    result = agent.find_bookkeepers(
        service=body.service,
        location=body.location,
        min_rating=body.min_rating,
    )
    result["payment_status"] = "received"
    result["payment_amount"] = "0.10 USDC"
    result["payment_network"] = "eip155:8453"
    return result


@app.get("/payment-info")
async def payment_info():
    return payment_middleware.get_payment_required_response()["payment"]


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
