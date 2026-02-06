#!/usr/bin/env python3
"""
Orchestrator - Runs all marketing bots in sequence
Master coordinator for ContractorFinder launch
"""

import sys
import os

# Add automation folder to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from twitter_bot import TwitterBot
from reddit_bot import RedditBot
from github_bot import GitHubBot
from x402_bazaar_bot import X402BazaarBot

class LaunchOrchestrator:
    """
    Orchestrates the complete launch of ContractorFinder
    Runs all marketing and submission bots
    """
    
    def __init__(self):
        self.bots = {
            "twitter": TwitterBot(),
            "reddit": RedditBot(),
            "github": GitHubBot(),
            "x402": X402BazaarBot()
        }
        self.results = {}
    
    def run_full_launch(self, dry_run: bool = True):
        """
        Run complete launch sequence
        
        Args:
            dry_run: If True, only print what would be done
        """
        print("🚀 CONTRACTORFINDER LAUNCH ORCHESTRATOR")
        print("=" * 60)
        print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
        print("=" * 60)
        
        # Phase 1: Social Media
        print("\n📱 PHASE 1: Social Media Marketing")
        print("-" * 60)
        
        print("\n1️⃣ Posting Twitter thread...")
        self.results["twitter"] = self.bots["twitter"].post_launch_thread()
        
        print("\n2️⃣ Posting to Reddit...")
        self.results["reddit"] = self.bots["reddit"].post_launch()
        
        # Phase 2: Registry Submissions
        print("\n📋 PHASE 2: Registry Submissions")
        print("-" * 60)
        
        print("\n3️⃣ Creating GitHub MCP Registry PR...")
        self.results["github_pr"] = self.bots["github"].create_registry_pr()
        
        print("\n4️⃣ Creating GitHub release...")
        self.results["github_release"] = self.bots["github"].create_repo_release()
        
        # Phase 3: x402 Ecosystem
        print("\n⛓️ PHASE 3: x402 Ecosystem")
        print("-" * 60)
        
        print("\n5️⃣ Submitting to x402 Bazaar...")
        self.results["x402"] = self.bots["x402"].submit_to_bazaar()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 LAUNCH SUMMARY")
        print("=" * 60)
        
        success_count = 0
        for name, result in self.results.items():
            status = result.get("status", "unknown")
            icon = "✅" if status in ["success", "ready", "mock"] else "❌"
            print(f"{icon} {name}: {status}")
            if status in ["success", "ready"]:
                success_count += 1
        
        print(f"\nCompleted: {success_count}/{len(self.results)} tasks")
        
        if dry_run:
            print("\n⚠️ This was a DRY RUN.")
            print("To execute for real, ensure all API credentials are set in .env:")
            print("  - TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET")
            print("  - REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD")
            print("  - GITHUB_TOKEN")
        
        return self.results
    
    def run_specific_bot(self, bot_name: str):
        """Run a specific bot only"""
        if bot_name not in self.bots:
            print(f"❌ Unknown bot: {bot_name}")
            print(f"Available: {', '.join(self.bots.keys())}")
            return
        
        print(f"🤖 Running {bot_name} bot...")
        
        if bot_name == "twitter":
            return self.bots[bot_name].post_launch_thread()
        elif bot_name == "reddit":
            return self.bots[bot_name].post_launch()
        elif bot_name == "github":
            return {
                "pr": self.bots[bot_name].create_registry_pr(),
                "release": self.bots[bot_name].create_repo_release()
            }
        elif bot_name == "x402":
            return self.bots[bot_name].submit_to_bazaar()

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ContractorFinder Launch Orchestrator")
    parser.add_argument(
        "--live", 
        action="store_true", 
        help="Execute live (not dry run)"
    )
    parser.add_argument(
        "--bot",
        choices=["twitter", "reddit", "github", "x402"],
        help="Run specific bot only"
    )
    
    args = parser.parse_args()
    
    orchestrator = LaunchOrchestrator()
    
    if args.bot:
        result = orchestrator.run_specific_bot(args.bot)
        print(json.dumps(result, indent=2))
    else:
        results = orchestrator.run_full_launch(dry_run=not args.live)
        
        if args.live:
            print("\n🎉 LIVE LAUNCH COMPLETE!")
        else:
            print("\n✅ DRY RUN COMPLETE")
            print("\nTo run live: python orchestrator.py --live")

if __name__ == "__main__":
    main()
