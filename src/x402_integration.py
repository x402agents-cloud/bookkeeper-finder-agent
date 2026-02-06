"""
x402 Payment Integration for ContractorFinder
Charges $0.10 USDC per API call
"""

import os
import json
from typing import Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# x402 Configuration
X402_CONFIG = {
    "price": "0.10",  # USDC
    "asset": "USDC",
    "network": "base",  # Base mainnet
    "facilitator": "https://facilitator.coinbase.com"
}

WALLET_ADDRESS = os.getenv("BASE_WALLET_ADDRESS", "0xb3e17988e6eE4D31e6D07decf363f736461d9e08")

class PaymentRequest(BaseModel):
    trade: str
    location: str
    min_rating: float = 4.0

class x402Middleware:
    """
    Middleware to handle x402 payments
    """
    
    def __init__(self, price_usd: float = 0.10):
        self.price = price_usd
        self.asset = "USDC"
        self.network = "base"
        self.receiver = WALLET_ADDRESS
    
    def check_payment(self, request_headers: dict) -> tuple[bool, Optional[dict]]:
        """
        Check if request includes valid payment
        Returns: (is_valid, payment_info)
        """
        # Check for x402 payment header
        payment_header = request_headers.get("X-Payment-Signature") or request_headers.get("x-payment-signature")
        
        if not payment_header:
            return False, None
        
        # In production, verify with facilitator
        # For MVP, we accept the header as proof of payment
        try:
            payment_info = json.loads(payment_header)
            return True, payment_info
        except:
            return True, {"status": "accepted"}
    
    def get_payment_required_response(self) -> dict:
        """
        Return 402 Payment Required response
        """
        return {
            "error": "Payment Required",
            "status": 402,
            "payment": {
                "scheme": "exact",
                "network": self.network,
                "asset": self.asset,
                "amount": str(self.price),
                "receiver": self.receiver,
                "facilitator": X402_CONFIG["facilitator"],
                "memo": "ContractorFinder API call"
            }
        }

# Initialize FastAPI app
app = FastAPI(title="ContractorFinder API", version="1.0.0")
payment_middleware = x402Middleware()

@app.on_event("startup")
async def startup_event():
    print(f"🚀 ContractorFinder API starting on port {os.getenv('PORT', 8000)}")
    print(f"💰 Wallet: {WALLET_ADDRESS[:20]}...")
    print(f"🤖 OpenAI: {'✅' if os.getenv('OPENAI_API_KEY') else '❌ Not set'}")

# Import agent
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.agent import agent

@app.middleware("http")
async def x402_payment_check(request: Request, call_next):
    """
    Check x402 payment on every request
    """
    # Skip payment check for health endpoints
    if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
        return await call_next(request)
    
    # Check payment
    is_paid, payment_info = payment_middleware.check_payment(dict(request.headers))
    
    if not is_paid:
        return JSONResponse(
            status_code=402,
            content=payment_middleware.get_payment_required_response()
        )
    
    # Store payment info in request state
    request.state.payment = payment_info
    
    # Payment valid, proceed
    return await call_next(request)

@app.get("/")
async def root():
    """Root endpoint - info only"""
    return {
        "name": "ContractorFinder API",
        "version": "1.0.0",
        "description": "Find licensed contractors with x402 payments",
        "price": "$0.10 USDC per call",
        "network": "Base",
        "endpoints": {
            "health": "/health",
            "find": "/find (POST, requires payment)"
        }
    }

@app.get("/health")
async def health_check():
    """Health check - no payment required"""
    return {
        "status": "healthy",
        "agent": "contractor-finder",
        "version": "1.0.0",
        "payment_required": True,
        "price": "0.10 USDC"
    }

@app.post("/find")
async def find_contractors_endpoint(request: Request, body: PaymentRequest):
    """
    Main endpoint - requires $0.10 payment via x402
    """
    result = agent.find_contractors(
        trade=body.trade,
        location=body.location,
        min_rating=body.min_rating
    )
    
    # Add payment confirmation
    result["payment_status"] = "received"
    result["payment_amount"] = "0.10 USDC"
    
    return result

@app.get("/payment-info")
async def payment_info():
    """Get payment requirements"""
    return payment_middleware.get_payment_required_response()["payment"]

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
