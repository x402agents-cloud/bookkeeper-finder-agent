# 🏠 ContractorFinder Agent

AI agent that finds licensed contractors with verified reviews. Built with x402 payments on Base blockchain.

## Features

- 🔍 **Search** licensed contractors by trade (plumber, electrician, roofer, HVAC, etc.)
- ✅ **Verify** license status (active, expired, suspended)
- ⭐ **Get reviews** and ratings from multiple sources
- 💰 **Pay per search** - $0.10 USDC via x402 protocol
- ⛓️ **Built on Base** - Fast, cheap, Ethereum L2
- 🛠️ **MCP compatible** - Works with Claude, GPT, and other AI assistants

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your API keys
nano .env
```

Required:
- `OPENAI_API_KEY` - For GPT-4 agent
- `APIFY_API_TOKEN` - For Google Maps data (optional, falls back to mock data)
- `BASE_WALLET_ADDRESS` - Your wallet to receive payments

Optional (for marketing bots):
- Twitter API keys
- Reddit API keys
- GitHub token

### 3. Test Locally

```bash
# Test the agent
python src/agent.py

# Test the API server
python src/x402_integration.py
```

### 4. Deploy

```bash
# Make deploy script executable
chmod +x deploy.sh

# Deploy to Railway
./deploy.sh
```

## API Usage

### Health Check (Free)

```bash
curl https://your-app.up.railway.app/health
```

### Find Contractors (Requires Payment)

```bash
curl -X POST https://your-app.up.railway.app/find \
  -H "Content-Type: application/json" \
  -H "X-Payment-Signature: <your_x402_payment>" \
  -d '{
    "trade": "plumber",
    "location": "Austin, TX",
    "min_rating": 4.0
  }'
```

### MCP Server

The agent can be used as an MCP tool with Claude or GPT:

```python
# In Claude Desktop config
{
  "mcpServers": {
    "contractor-finder": {
      "command": "python",
      "args": ["/path/to/src/mcp_server.py"]
    }
  }
}
```

## Pricing

- **$0.10 USDC** per search
- Pay only when you find contractors worth contacting
- No subscription, no hidden fees
- Payments settle instantly on Base

## Marketing Automation

Launch marketing across all platforms:

```bash
# Dry run (see what would be posted)
python automation/orchestrator.py

# Live launch (requires API credentials)
python automation/orchestrator.py --live
```

Individual bots:

```bash
python automation/twitter_bot.py      # Post Twitter thread
python automation/reddit_bot.py       # Post to subreddits
python automation/github_bot.py       # Create MCP registry PR
python automation/x402_bazaar_bot.py  # Submit to x402 Bazaar
```

## Architecture

```
┌─────────────────┐
│   User Request  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  x402 Payment   │ ← $0.10 USDC on Base
│   Verification  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  GPT-4 Agent    │ ← Natural language understanding
│  (agent.py)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Data Sources   │ ← Apify/Google Maps
│  + License API  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Top 3 Results  │ ← Verified, rated contractors
│  with contact   │
└─────────────────┘
```

## File Structure

```
contractor-finder-agent/
├── src/
│   ├── agent.py              # Core agent logic
│   ├── mcp_server.py         # MCP protocol wrapper
│   └── x402_integration.py   # Payment middleware
├── automation/
│   ├── twitter_bot.py        # Twitter marketing
│   ├── reddit_bot.py         # Reddit marketing
│   ├── github_bot.py         # MCP registry PR
│   ├── x402_bazaar_bot.py    # x402 submission
│   └── orchestrator.py       # Master coordinator
├── deploy.sh                 # Deployment script
├── Dockerfile               # Container config
├── Procfile                 # Railway config
├── requirements.txt         # Python deps
└── .env                     # Environment vars
```

## Revenue Model

| Metric | Value |
|--------|-------|
| Price per search | $0.10 USDC |
| Hosting cost | ~$20/month |
| Break-even | 200 searches/month |
| 1,000 searches/month | $100 revenue / $80 profit |
| 10,000 searches/month | $1,000 revenue / $980 profit |

## Roadmap

- [x] Core agent functionality
- [x] x402 payment integration
- [x] MCP server
- [x] Marketing automation
- [ ] Real license verification APIs (state-by-state)
- [ ] Review aggregation from Yelp, Angi, etc.
- [ ] Booking/scheduling integration
- [ ] Insurance verification
- [ ] Multi-language support

## License

MIT - See LICENSE file

## Support

- Documentation: This README
- Issues: GitHub Issues
- x402: https://www.x402.org
- MCP: https://modelcontextprotocol.io

---

Built with ❤️ on [Base](https://base.org) using [x402](https://www.x402.org)
