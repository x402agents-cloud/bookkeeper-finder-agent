"""
Reddit Bot for ContractorFinder Agent Marketing
Posts to relevant subreddits
"""

import os
import time
from typing import List, Dict

try:
    import praw
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False
    print("Warning: praw not installed. Using mock mode.")

class RedditBot:
    """
    Posts about ContractorFinder to relevant subreddits
    """
    
    TARGET_SUBREDDITS = [
        "r/SideProject",
        "r/SaaS",
        "r/Entrepreneur",
        "r/webdev",
        "r/ArtificialInteligence"
    ]
    
    def __init__(self):
        self.client_id = os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.username = os.getenv("REDDIT_USERNAME")
        self.password = os.getenv("REDDIT_PASSWORD")
        self.user_agent = "ContractorFinder Bot v1.0"
        
        self.reddit = None
        if PRAW_AVAILABLE and all([self.client_id, self.client_secret, self.username, self.password]):
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                username=self.username,
                password=self.password,
                user_agent=self.user_agent
            )
    
    def post_to_subreddit(self, subreddit: str, title: str, body: str) -> Dict:
        """Post to a specific subreddit"""
        if not self.reddit:
            print(f"\nWould post to {subreddit}:")
            print(f"Title: {title}")
            print(f"Body: {body[:200]}...")
            return {"status": "mock", "subreddit": subreddit}
        
        try:
            sub = self.reddit.subreddit(subreddit.replace("r/", ""))
            submission = sub.submit(title=title, selftext=body)
            
            return {
                "status": "success",
                "subreddit": subreddit,
                "post_id": submission.id,
                "url": f"https://reddit.com{submission.permalink}"
            }
            
        except Exception as e:
            return {"status": "error", "subreddit": subreddit, "error": str(e)}
    
    def post_launch(self) -> List[Dict]:
        """Post launch announcement to all target subreddits"""
        
        posts = [
            {
                "subreddit": "r/SideProject",
                "title": "I built an AI agent that finds licensed contractors - charges $0.10 per search via crypto payments",
                "body": """Hey r/SideProject!

I just shipped ContractorFinder - an AI agent that solves a real problem: finding licensed contractors.

**The Problem:**
• 40% of "contractors" aren't actually licensed
• Reviews are scattered across 5 different sites
• You waste hours calling dead numbers
• No easy way to verify license status

**The Solution:**
ContractorFinder is an AI agent that:
✅ Searches licensed contractors by trade & location
✅ Verifies license status (active/expired/suspended)
✅ Pulls real reviews & ratings
✅ Returns top 3 with contact info

**The Tech:**
• GPT-4 for natural language queries
• Google Maps + Apify for contractor data
• License verification via state APIs
• Built on Base blockchain with x402 payments
• MCP protocol compatible (works with Claude/GPT)

**Pricing:**
$0.10 USDC per search. Pay only when you find someone worth calling.

**Live now:** https://ca-contractor-finder-production.up.railway.app

Built this in about 4 hours. Would love feedback!

What other "boring but useful" agents should I build?"""
            },
            {
                "subreddit": "r/SaaS",
                "title": "Launched: AI-powered contractor finder with crypto micropayments",
                "body": """Just launched a micro-SaaS that finds licensed contractors using AI.

**Revenue model:** $0.10 per API call, paid in USDC on Base.

Why crypto payments?
• No chargebacks
• Instant settlement
• Works globally
• 0.5% fees vs 2.9% + $0.30 for Stripe

The tech stack:
• FastAPI backend
• GPT-4 for query understanding
• x402 payment protocol
• Deployed on Railway

Target market: Homeowners, property managers, real estate investors

Looking for beta users. Try it free (first 3 searches).

Thoughts on the crypto payment model for SaaS?"""
            },
            {
                "subreddit": "r/ArtificialInteligence",
                "title": "Built an agent that hires contractors - uses x402 for autonomous payments",
                "body": """ContractorFinder: An AI agent that finds, verifies, and ranks licensed contractors.

The interesting part: It uses x402 protocol for payments, meaning agents can pay agents autonomously.

Example:
1. User asks Claude: "Find me a plumber in Austin"
2. Claude calls ContractorFinder via MCP
3. ContractorFinder charges $0.10 USDC
4. Returns verified plumber with reviews

No human in the loop for payment.

This is the beginning of agent economies - AIs hiring AIs, paying each other in crypto.

Try it: https://ca-contractor-finder-production.up.railway.app

Docs: https://github.com/yourname/contractor-finder-agent

What do you think? Will agents paying agents be the killer use case for crypto?"""
            }
        ]
        
        results = []
        for post in posts:
            print(f"\n📝 Posting to {post['subreddit']}...")
            result = self.post_to_subreddit(
                post["subreddit"],
                post["title"],
                post["body"]
            )
            results.append(result)
            
            if result["status"] == "success":
                print(f"✅ Posted: {result['url']}")
            elif result["status"] == "mock":
                print(f"✅ Mock mode: Ready to post")
            else:
                print(f"❌ Error: {result.get('error')}")
            
            time.sleep(5)  # Rate limit protection
        
        return results

def main():
    """Run the Reddit bot"""
    bot = RedditBot()
    
    print("🤖 Reddit Bot for ContractorFinder")
    print("=" * 50)
    
    results = bot.post_launch()
    
    successful = sum(1 for r in results if r["status"] == "success")
    print(f"\n✅ Posted to {successful}/{len(results)} subreddits")
    
    if any(r["status"] == "mock" for r in results):
        print("\nTo post for real, set Reddit API credentials in .env:")
        print("  REDDIT_CLIENT_ID")
        print("  REDDIT_CLIENT_SECRET")
        print("  REDDIT_USERNAME")
        print("  REDDIT_PASSWORD")

if __name__ == "__main__":
    main()
