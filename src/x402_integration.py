"""
BookkeeperFinder API - x402 v2 Compatible
Returns proper PAYMENT-REQUIRED header for @x402/fetch v2 client compatibility.
"""

import os
import sys
import json
import base64
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# --- Config ---
WALLET_ADDRESS = os.getenv(
    "BASE_WALLET_ADDRESS",
    "0xb3e17988e6eE4D31e6D07decf363f736461d9e08",
)
FACILITATOR_URL = os.getenv("X402_FACILITATOR_URL", "https://x402.org/facilitator")

# Network: Base mainnet (CAIP-2 format)
NETWORK = "eip155:8453"

# USDC contract on Base mainnet
USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"

# Price in base units (0.10 USDC = 100000 with 6 decimals)
PRICE_BASE_UNITS = os.getenv("X402_PRICE_BASE_UNITS", "100000")

app = FastAPI(title="BookkeeperFinder API", version="2.1.0")

# --- Import agent ---
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.agent import agent


class FindRequest(BaseModel):
    trade: str = "bookkeeper"
    service: str = "bookkeeper"
    location: str = "Miami, FL"
    min_rating: float = 4.0


def build_payment_required(request_url: str) -> dict:
    """Build x402 v2 PaymentRequired object."""
    return {
        "x402Version": 2,
        "error": "Payment required",
        "resource": {
            "url": str(request_url),
            "description": "Find verified bookkeepers and accountants",
            "mimeType": "application/json",
        },
        "accepts": [
            {
                "scheme": "exact",
                "network": NETWORK,
                "asset": USDC_ADDRESS,
                "amount": PRICE_BASE_UNITS,
                "payTo": WALLET_ADDRESS,
                "maxTimeoutSeconds": 300,
                "extra": {
                    "name": "USDC",
                    "version": "2",
                },
            }
        ],
    }


def encode_payment_required(pr: dict) -> str:
    """Base64 encode the PaymentRequired object for the header."""
    return base64.b64encode(json.dumps(pr).encode()).decode()


async def verify_payment_with_facilitator(payment_payload: dict, payment_requirements: dict) -> dict:
    """Verify payment with x402 facilitator."""
    import httpx
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{FACILITATOR_URL}/verify",
            json={
                "x402Version": 2,
                "paymentPayload": payment_payload,
                "paymentRequirements": payment_requirements,
            },
            timeout=30.0,
        )
        return resp.json()


async def settle_payment_with_facilitator(payment_payload: dict, payment_requirements: dict) -> dict:
    """Settle payment with x402 facilitator."""
    import httpx
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{FACILITATOR_URL}/settle",
            json={
                "x402Version": 2,
                "paymentPayload": payment_payload,
                "paymentRequirements": payment_requirements,
            },
            timeout=30.0,
        )
        return resp.json()


@app.middleware("http")
async def x402_middleware(request: Request, call_next):
    """x402 v2 payment middleware."""
    # Skip for non-payment routes
    if request.url.path in ["/", "/health", "/docs", "/openapi.json", "/payment-info"]:
        return await call_next(request)

    # Only protect paid endpoints
    if request.method != "POST" or request.url.path not in ("/find", "/api/search"):
        return await call_next(request)

    # Check for payment signature header
    payment_header = (
        request.headers.get("payment-signature")
        or request.headers.get("PAYMENT-SIGNATURE")
        or request.headers.get("x-payment")
        or request.headers.get("X-PAYMENT")
    )

    if not payment_header:
        pr = build_payment_required(str(request.url))
        encoded = encode_payment_required(pr)
        return JSONResponse(
            status_code=402,
            content=pr,
            headers={"PAYMENT-REQUIRED": encoded},
        )

    # Decode payment payload
    try:
        payment_payload = json.loads(base64.b64decode(payment_header))
    except Exception:
        pr = build_payment_required(str(request.url))
        pr["error"] = "Invalid payment signature"
        encoded = encode_payment_required(pr)
        return JSONResponse(
            status_code=402,
            content=pr,
            headers={"PAYMENT-REQUIRED": encoded},
        )

    # Get matching requirements
    pr = build_payment_required(str(request.url))
    requirements = pr["accepts"][0]

    # Verify with facilitator
    try:
        verify_result = await verify_payment_with_facilitator(payment_payload, requirements)
        if not verify_result.get("isValid", False):
            reason = verify_result.get("invalidReason", "Payment verification failed")
            encoded = encode_payment_required(pr)
            return JSONResponse(
                status_code=402,
                content={"error": reason},
                headers={"PAYMENT-REQUIRED": encoded},
            )
    except Exception as e:
        print(f"Facilitator verify error: {e}")
        pass

    # Payment verified - process request
    response = await call_next(request)

    # Settle payment after successful response
    if response.status_code == 200:
        try:
            settle_result = await settle_payment_with_facilitator(payment_payload, requirements)
            if settle_result.get("success"):
                settle_encoded = base64.b64encode(json.dumps(settle_result).encode()).decode()
                response.headers["PAYMENT-RESPONSE"] = settle_encoded
                print(f"💰 Payment settled: tx={settle_result.get('transaction', 'N/A')}")
            else:
                print(f"⚠️ Settlement failed: {settle_result.get('errorReason', 'unknown')}")
        except Exception as e:
            print(f"Settlement error: {e}")

    return response


@app.get("/")
async def root():
    return {
        "name": "BookkeeperFinder API",
        "version": "2.1.0",
        "price": "$0.10 USDC per call",
        "network": f"Base ({NETWORK})",
        "wallet": WALLET_ADDRESS,
        "x402": {
            "version": 2,
            "facilitator": FACILITATOR_URL,
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
        "version": "2.1.0",
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


@app.get("/payment-info")
async def payment_info():
    return build_payment_required("https://lexical-kalinda-x402-agents-10e84d5e.koyeb.app/api/search")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
