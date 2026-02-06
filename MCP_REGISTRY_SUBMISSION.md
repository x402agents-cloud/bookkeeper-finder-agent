# BookkeeperFinder MCP Server Submission

## Overview

BookkeeperFinder is an MCP (Model Context Protocol) server that enables AI agents to find certified bookkeepers and CPAs instantly. All professionals are verified with state licensing boards.

## Key Features

- ✅ **950 verified bookkeepers** across 37 cities
- ✅ **License verification** with state CPA boards
- ✅ **Real reviews and ratings**
- ✅ **QuickBooks certified** professionals
- ✅ **$0.10 per search** via x402 payments
- ✅ **10 second response time**

## Data Coverage

### Florida (350 bookkeepers)
- Miami, Tampa, Orlando
- Fort Lauderdale, Jacksonville
- St. Petersburg, West Palm Beach

### Nationwide (600 bookkeepers)
- New York, Los Angeles, Chicago
- Houston, Phoenix, Philadelphia
- 30+ additional major cities

## Use Cases

- Small business owners needing bookkeeping
- Real estate investors tracking expenses
- Freelancers needing tax preparation
- Startups setting up accounting systems
- Anyone switching from DIY to professional accounting

## Technical Details

- **Runtime:** Python 3.11+
- **Framework:** FastAPI + MCP
- **Payments:** x402 protocol (USDC on Base)
- **Data:** Curated from state CPA boards + AICPA
- **Verification:** License status checked

## API Example

```python
# Search for bookkeepers in Miami
response = await mcp_client.call_tool(
    "bookkeeper-finder",
    "search",
    {
        "service": "bookkeeping",
        "location": "Miami, FL",
        "min_rating": 4.0
    }
)

# Returns verified bookkeepers with:
# - Name, phone, address
# - License number and status
# - Ratings and reviews
# - Services offered
# - QuickBooks certification
```

## Why This Matters

Finding a reliable bookkeeper is hard:
- Many claim credentials they don't have
- Reviews can be fake
- Pricing is often unclear
- Response times are slow

BookkeeperFinder solves this by:
- Verifying all licenses with state boards
- Providing instant results
- Charging only when you find someone ($0.10)
- Making data available to AI agents

## Repository

https://github.com/x402agents-cloud/bookkeeper-finder-agent

## License

MIT

## Contact

Twitter: @X402AgentStudio
GitHub: x402agents-cloud
