"""
BookkeeperFinder API - x402 SDK with Bazaar Discovery
Uses official x402 Python SDK PaymentMiddlewareASGI
"""

import os
import sys
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

from x402.http import FacilitatorConfig, HTTPFacilitatorClient, PaymentOption
from x402.http.middleware.fastapi import PaymentMiddlewareASGI
from x402.http.types import RouteConfig
from x402.mechanisms.evm.exact import ExactEvmServerScheme
from x402.server import x402ResourceServer

# --- Config ---
WALLET_ADDRESS = os.getenv(
    "BASE_WALLET_ADDRESS",
    "0xb3e17988e6eE4D31e6D07decf363f736461d9e08",
)
FACILITATOR_URL = os.getenv("X402_FACILITATOR_URL", "https://www.x402.org/facilitator")
NETWORK = "eip155:84532"

app = FastAPI(title="BookkeeperFinder API", version="3.0.0")

# --- Import agent ---
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.agent import agent

# --- x402 SDK setup ---
facilitator = HTTPFacilitatorClient(FacilitatorConfig(url=FACILITATOR_URL))
server = x402ResourceServer(facilitator)
server.register("eip155:84532", ExactEvmServerScheme())

routes = {
    "POST /api/search": RouteConfig(
        accepts=[PaymentOption(scheme="exact", pay_to=WALLET_ADDRESS, price="$0.10", network=NETWORK)],
        mime_type="application/json",
        description="Find verified bookkeepers and accountants",
        extensions={
            "bazaar": {
                "info": {
                    "input": {"specialty": "bookkeeper", "location": "Miami, FL"},
                    "output": {
                        "type": "json",
                        "example": {
                            "results": [{"name": "Example Bookkeeper", "license_number": "BK123", "rating": 4.8}],
                            "count": 1,
                        },
                    },
                },
            },
        },
    ),
    "POST /find": RouteConfig(
        accepts=[PaymentOption(scheme="exact", pay_to=WALLET_ADDRESS, price="$0.10", network=NETWORK)],
        mime_type="application/json",
        description="Find verified bookkeepers and accountants",
        extensions={
            "bazaar": {
                "info": {
                    "input": {"specialty": "bookkeeper", "location": "Miami, FL"},
                    "output": {
                        "type": "json",
                        "example": {
                            "results": [{"name": "Example Bookkeeper", "license_number": "BK123", "rating": 4.8}],
                            "count": 1,
                        },
                    },
                },
            },
        },
    ),
}

app.add_middleware(PaymentMiddlewareASGI, routes=routes, server=server)


class FindRequest(BaseModel):
    trade: str = "bookkeeper"
    service: str = "bookkeeper"
    location: str = "Miami, FL"
    min_rating: float = 4.0


@app.get("/")
async def root():
    return {
        "name": "BookkeeperFinder API",
        "version": "3.0.0",
        "price": "$0.10 USDC per call",
        "network": f"Base Sepolia ({NETWORK})",
        "wallet": WALLET_ADDRESS,
        "x402": {
            "version": 2,
            "sdk": "x402[fastapi]",
            "facilitator": FACILITATOR_URL,
            "bazaar": True,
        },
        "endpoints": {
            "health": "/health",
            "find": "POST /find (requires $0.10 USDC payment via x402)",
            "search": "POST /api/search (requires $0.10 USDC payment via x402)",
        },
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "agent": "bookkeeper-finder",
        "version": "3.0.0",
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
