"""
x402 Bazaar Bot for ContractorFinder Agent
Submits service to x402 ecosystem
"""

import os
import json
import requests
from typing import Dict

class X402BazaarBot:
    """
    Submits ContractorFinder to x402 Bazaar ecosystem
    """
    
    BAZAAR_URL = "https://www.x402.org/ecosystem"
    
    def __init__(self):
        self.wallet_address = os.getenv("BASE_WALLET_ADDRESS", "0xb3e17988e6eE4D31e6D07decf363f736461d9e08")
        self.api_endpoint = os.getenv("API_ENDPOINT", "https://ca-contractor-finder-production.up.railway.app")
    
    def generate_submission(self) -> Dict:
        """
        Generate submission data for x402 Bazaar
        """
        return {
            "name": "ContractorFinder",
            "description": "AI agent that finds licensed contractors with verified reviews. Charges $0.10 USDC per search.",
            "category": "AI Agent",
            "tags": ["contractors", "licenses", "reviews", "AI", "MCP"],
            "pricing": {
                "model": "per-request",
                "amount": "0.10",
                "currency": "USDC",
                "network": "base"
            },
            "endpoint": self.api_endpoint,
            "wallet_address": self.wallet_address,
            "protocols": ["x402", "MCP"],
            "documentation": "https://github.com/yourname/contractor-finder-agent",
            "status": "live"
        }
    
    def submit_to_bazaar(self) -> Dict:
        """
        Submit to x402 Bazaar
        Note: Bazaar may require manual submission via web form
        """
        submission = self.generate_submission()
        
        print("📝 x402 Bazaar Submission")
        print("=" * 50)
        print(json.dumps(submission, indent=2))
        print("=" * 50)
        
        print(f"\n📤 Submit to: {self.BAZAAR_URL}")
        print("\nCopy the above JSON and submit via the web form.")
        print("Or tweet it with #x402 #BuildOnBase hashtags!")
        
        return {
            "status": "ready",
            "submission": submission,
            "submit_url": self.BAZAAR_URL
        }
    
    def generate_tweet(self) -> str:
        """Generate tweet for x402 Bazaar announcement"""
        return """🚀 Just listed on x402 Bazaar!

ContractorFinder - AI agent that finds licensed contractors

• $0.10 per search (USDC on @base)
• MCP compatible
• Verifies licenses & reviews

Agents paying agents. The future is here.

Try it: https://ca-contractor-finder-production.up.railway.app

#x402 #BuildOnBase #AIagent"""
    
    def verify_x402_setup(self) -> Dict:
        """Verify x402 payment setup is working"""
        
        print("🔍 Verifying x402 setup...")
        
        checks = {
            "wallet_address": self.wallet_address,
            "wallet_configured": self.wallet_address != "0xYourWalletAddress",
            "api_endpoint": self.api_endpoint,
            "endpoint_live": False
        }
        
        # Check if endpoint is live
        try:
            response = requests.get(f"{self.api_endpoint}/health", timeout=10)
            checks["endpoint_live"] = response.status_code == 200
            checks["health_response"] = response.json()
        except Exception as e:
            checks["endpoint_error"] = str(e)
        
        return checks

def main():
    """Run the x402 Bazaar bot"""
    bot = X402BazaarBot()
    
    print("🌐 x402 Bazaar Bot for ContractorFinder")
    print("=" * 50)
    
    # Verify setup
    print("\n🔍 Checking x402 setup...")
    checks = bot.verify_x402_setup()
    
    if checks["wallet_configured"]:
        print(f"✅ Wallet configured: {checks['wallet_address'][:20]}...")
    else:
        print("⚠️ Wallet not properly configured")
    
    if checks["endpoint_live"]:
        print(f"✅ API endpoint live: {checks['api_endpoint']}")
    else:
        print(f"⚠️ API endpoint not responding")
    
    # Generate submission
    print("\n📋 Generating Bazaar submission...")
    result = bot.submit_to_bazaar()
    
    # Generate tweet
    print("\n🐦 Suggested tweet:")
    print(bot.generate_tweet())

if __name__ == "__main__":
    main()
