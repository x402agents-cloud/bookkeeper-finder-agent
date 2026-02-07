"""
BookkeeperFinder API - x402 v2 with Bazaar Discovery
"""

import os
import sys
from typing import Any

from fastapi import FastAPI, Request
from pydantic import BaseModel

from x402.http import FacilitatorConfig, HTTPFacilitatorClient, PaymentOption
from x402.http.middleware.fastapi import PaymentMiddlewareASGI
from x402.http.types import RouteConfig
from x402.mechanisms.evm.exact import ExactEvmServerScheme
from x402.server import x402ResourceServer

# --- Config ---
WALLET_ADDRESS = os.getenv(
    "BASE_WALLET_ADDRESS",
    "0x708AF34B155834B1e45B4B4b5933486a4e173C4e",
)
FACILITATOR_URL = os.getenv("X402_FACILITATOR_URL", "https://x402.org/facilitator")

# --- FastAPI App ---
app = FastAPI(title="BookkeeperFinder API", version="2.0.0")

# --- x402 Resource Server ---
facilitator = HTTPFacilitatorClient(FacilitatorConfig(url=FACILITATOR_URL))
server = x402ResourceServer(facilitator)
server.register("eip155:8453", ExactEvmServerScheme())

# --- Routes with Bazaar discovery metadata ---
routes: dict[str, RouteConfig] = {
    "POST /find": RouteConfig(
        accepts=[
            PaymentOption(
                scheme="exact",
                pay_to=WALLET_ADDRESS,
                price="$0.10",
                network="eip155:8453",
            ),
        ],
        mime_type="application/json",
        description="Find certified bookkeepers and CPAs. Verifies CPA licenses (California), QuickBooks certification.",
        extensions={
            "bazaar": {
                "info": {
                    "input": {
                        "type": "json",
                        "example": {
                            "service": "bookkeeper",
                            "location": "Los Angeles, CA",
                            "min_rating": 4.0,
                        },
                        "schema": {
                            "type": "object",
                            "properties": {
                                "service": {"type": "string", "description": "Service type (bookkeeper, CPA, tax preparer)"},
                                "location": {"type": "string", "description": "City and state"},
                                "min_rating": {"type": "number", "description": "Minimum rating 1-5", "default": 4.0},
                            },
                            "required": ["service", "location"],
                        },
                    },
                    "output": {
                        "type": "json",
                        "example": {
                            "query": {"service": "bookkeeper", "location": "Los Angeles, CA", "min_rating": 4.0},
                            "results": [
                                {
                                    "name": "Elite Accounting",
                                    "license_number": "CPA-45678",
                                    "license_status": "ACTIVE",
                                    "phone": "555-1234",
                                    "rating": 4.8,
                                    "review_count": 87,
                                    "verified": True,
                                    "quickbooks_certified": True,
                                    "services": ["Bookkeeping", "Tax Preparation", "QuickBooks Certified"],
                                }
                            ],
                            "count": 1,
                            "price_charged": 0.10,
                            "data_sources": ["Local Database", "CBA (CA)", "QuickBooks"],
                        },
                    },
                },
            },
        },
    ),
}

app.add_middleware(PaymentMiddlewareASGI, routes=routes, server=server)

# --- Import agent ---
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.agent import agent


class FindRequest(BaseModel):
    service: str
    location: str
    min_rating: float = 4.0


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
    return {
        "scheme": "exact",
        "network": "eip155:8453",
        "asset": "USDC",
        "amount": "0.10",
        "receiver": WALLET_ADDRESS,
        "facilitator": FACILITATOR_URL,
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
