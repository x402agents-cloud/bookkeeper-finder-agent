"""
Twitter Bot for ContractorFinder Agent Marketing
Posts threads about the agent to Twitter/X
"""

import os
import json
import time
from typing import List, Dict

# Try to import tweepy, fallback to requests if not available
try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False
    print("Warning: tweepy not installed. Using mock mode.")

class TwitterBot:
    """
    Posts marketing content for ContractorFinder to Twitter
    """
    
    def __init__(self):
        self.api_key = os.getenv("TWITTER_API_KEY")
        self.api_secret = os.getenv("TWITTER_API_SECRET")
        self.access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_secret = os.getenv("TWITTER_ACCESS_SECRET")
        
        self.client = None
        if TWEEPY_AVAILABLE and all([self.api_key, self.api_secret, self.access_token, self.access_secret]):
            auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
            auth.set_access_token(self.access_token, self.access_secret)
            self.client = tweepy.API(auth)
    
    def post_launch_thread(self) -> Dict:
        """
        Post the main launch thread about ContractorFinder
        """
        tweets = [
            "🚀 Just launched: ContractorFinder - an AI agent that finds licensed contractors in your area\n\nNo more guessing. No more unlicensed hacks.\n\nReal contractors. Real reviews. Real licenses verified.\n\nBuilt on @base with x402 payments 🧵",
            "What it does:\n\n✅ Searches licensed contractors by trade\n✅ Verifies license status (active/expired)\n✅ Pulls real reviews & ratings\n✅ Returns top 3 with contact info\n✅ Charges $0.10 per search (USDC on Base)\n\nPay only when you find someone worth calling",
            "Why I built this:\n\nHiring contractors is broken.\n\n• 40% of 'contractors' aren't licensed\n• Reviews are scattered across 5 sites\n• You waste hours calling dead numbers\n\nContractorFinder fixes all of it in one API call",
            "Tech stack:\n\n🤖 GPT-4 for natural language queries\n🔍 Google Maps + Apify for data\n✅ License verification (state APIs)\n⛓️ x402 payments on @base\n🛠️ MCP protocol compatible\n\nAgents paying agents. The future.",
            "Try it:\n\nEndpoint: https://ca-contractor-finder-production.up.railway.app\nPrice: $0.10 USDC per search\nNetwork: @base\n\nOr use it via MCP in Claude/GPT\n\nDocs: https://github.com/yourname/contractor-finder-agent\n\nBuilt in 4 hours. Live now. 🎉"
        ]
        
        if not self.client:
            print("Twitter credentials not configured. Printing tweets instead:")
            for i, tweet in enumerate(tweets, 1):
                print(f"\n--- Tweet {i} ---")
                print(tweet)
            return {"status": "mock", "tweets": len(tweets)}
        
        # Post thread
        try:
            last_tweet_id = None
            posted = []
            
            for tweet in tweets:
                if last_tweet_id:
                    response = self.client.update_status(
                        status=tweet,
                        in_reply_to_status_id=last_tweet_id,
                        auto_populate_reply_metadata=True
                    )
                else:
                    response = self.client.update_status(status=tweet)
                
                last_tweet_id = response.id
                posted.append(response.id)
                time.sleep(2)  # Rate limit protection
            
            return {
                "status": "success",
                "tweet_ids": posted,
                "count": len(posted)
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def post_update(self, message: str) -> Dict:
        """Post a single update"""
        if not self.client:
            print(f"Would tweet: {message}")
            return {"status": "mock"}
        
        try:
            response = self.client.update_status(status=message)
            return {"status": "success", "tweet_id": response.id}
        except Exception as e:
            return {"status": "error", "error": str(e)}

def main():
    """Run the Twitter bot"""
    bot = TwitterBot()
    
    print("🐦 Twitter Bot for ContractorFinder")
    print("=" * 50)
    
    # Post launch thread
    result = bot.post_launch_thread()
    
    if result["status"] == "success":
        print(f"✅ Posted thread with {result['count']} tweets")
    elif result["status"] == "mock":
        print(f"\n✅ Mock mode: {result['tweets']} tweets ready to post")
        print("\nTo post for real, set Twitter API credentials in .env:")
        print("  TWITTER_API_KEY")
        print("  TWITTER_API_SECRET")
        print("  TWITTER_ACCESS_TOKEN")
        print("  TWITTER_ACCESS_SECRET")
    else:
        print(f"❌ Error: {result.get('error')}")

if __name__ == "__main__":
    main()
