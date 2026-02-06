# 🚀 ContractorFinder Launch Guide
## Complete Deployment & Launch Checklist

**Goal:** Deploy agent to Railway, register on Base blockchain, and get payment proof

---

## Phase 1: Pre-Flight Checks (5 minutes)

### 1.1 Verify Environment Variables

```bash
cd ~/contractor-finder-agent

# Check .env file
cat .env
```

**Required:**
- [ ] `OPENAI_API_KEY` — Your OpenAI API key (starts with `sk-`)
- [ ] `APIFY_API_TOKEN` — Already set (real token)
- [ ] `BASE_WALLET_ADDRESS` — Already set

**Optional (for marketing):**
- [ ] Twitter API keys
- [ ] Reddit API credentials
- [ ] GitHub token

### 1.2 Install Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 1.3 Test Locally

```bash
# Test agent logic
python3 -c "from src.agent import agent; result = agent.find_contractors('plumber', 'Austin, TX'); print('✅ Agent works:', result['count'], 'found')"

# Should output: "✅ Agent works: 5 found"
```

**If successful → Proceed to Phase 2**

---

## Phase 2: Deploy to Railway (10 minutes)

### 2.1 Install Railway CLI (if not installed)

```bash
npm install -g @railway/cli
```

### 2.2 Login to Railway

```bash
railway login
# This opens browser for authentication
```

### 2.3 Run Deploy Script

```bash
# Make sure OPENAI_API_KEY is exported
export OPENAI_API_KEY="sk-your-key-here"

# Run deployment
./deploy.sh
```

**What the script does:**
1. ✅ Checks environment
2. ✅ Tests agent locally
3. ✅ Initializes Railway project (first time)
4. ✅ Deploys to Railway
5. ✅ Verifies health endpoint

### 2.4 Verify Deployment

```bash
# Get your Railway URL
railway domain
# Output: https://contractor-finder.up.railway.app (or similar)

# Test health endpoint
curl https://YOUR-APP.up.railway.app/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "agent": "contractor-finder",
  "version": "1.0.0",
  "payment_required": true,
  "price": "0.10 USDC"
}
```

✅ **PHASE 2 COMPLETE** — Agent is live!

---

## Phase 3: Fund Base Wallet (5 minutes)

### 3.1 Check Wallet Address

Your wallet: `0xb3e17988e6eE4D31e6D07decf363f736461d9e08`

View on BaseScan: https://basescan.org/address/0xb3e17988e6eE4D31e6D07decf363f736461d9e08

### 3.2 Add USDC to Wallet

**Option A: Transfer from Coinbase/Exchange**
1. Buy USDC on Coinbase
2. Send to your wallet address (Base network)
3. Start with $10-20 for testing

**Option B: Bridge from Ethereum**
1. Go to https://bridge.base.org
2. Connect wallet
3. Bridge USDC from Ethereum to Base

**Option C: On-ramp directly**
1. Use Coinbase Wallet app
2. Buy USDC directly on Base

### 3.3 Verify Funds

```bash
# Check balance on BaseScan
open https://basescan.org/address/0xb3e17988e6eE4D31e6D07decf363f736461d9e08

# Look for USDC balance (should show > 0)
```

---

## Phase 4: Test Payment Flow (10 minutes)

### 4.1 Test Without Payment (Should Fail)

```bash
# This should return 402 Payment Required
curl -X POST https://YOUR-APP.up.railway.app/find \
  -H "Content-Type: application/json" \
  -d '{"trade": "plumber", "location": "Austin, TX"}'
```

**Expected:**
```json
{
  "error": "Payment Required",
  "status": 402,
  "payment": {
    "scheme": "exact",
    "network": "base",
    "asset": "USDC",
    "amount": "0.10",
    "receiver": "0xb3e17988e6eE4D31e6D07decf363f736461d9e08",
    "facilitator": "https://facilitator.coinbase.com"
  }
}
```

✅ **Payment middleware working!**

### 4.2 Test With Payment (Should Succeed)

```bash
# Mock payment header (MVP accepts any header)
curl -X POST https://YOUR-APP.up.railway.app/find \
  -H "Content-Type: application/json" \
  -H "X-Payment-Signature: {\"mock\": \"payment\"}" \
  -d '{"trade": "plumber", "location": "Austin, TX"}'
```

**Expected:**
```json
{
  "query": {"trade": "plumber", "location": "Austin, TX", "min_rating": 4.0},
  "results": [...],
  "count": 5,
  "price_charged": 0.10,
  "timestamp": "2026-02-06T...",
  "payment_status": "received",
  "payment_amount": "0.10 USDC"
}
```

✅ **Full flow working!**

---

## Phase 5: Deploy ERC-8004 Identity (Optional - 15 minutes)

### 5.1 Install Hardhat

```bash
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox
npx hardhat init
# Choose: Create a TypeScript project
```

### 5.2 Configure Hardhat for Base

**hardhat.config.ts:**
```typescript
import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";

const config: HardhatUserConfig = {
  solidity: "0.8.19",
  networks: {
    baseSepolia: {
      url: "https://sepolia.base.org",
      accounts: [process.env.PRIVATE_KEY!],
    },
    baseMainnet: {
      url: "https://mainnet.base.org",
      accounts: [process.env.PRIVATE_KEY!],
    },
  },
};

export default config;
```

### 5.3 Deploy Registry Contract

```bash
# Set your private key (from MetaMask/Coinbase Wallet)
export PRIVATE_KEY="0x..."

# Deploy to Base Sepolia (testnet) first
npx hardhat run scripts/deploy-erc8004.js --network baseSepolia

# Then deploy to Base Mainnet
npx hardhat run scripts/deploy-erc8004.js --network baseMainnet
```

**Save the deployed contract address!**

### 5.4 Upload Metadata to IPFS

```bash
# Install Pinata CLI
npm install -g @pinata/sdk

# Upload metadata
pinata pin-file erc8004-metadata.json

# Save the IPFS hash (Qm...)
```

### 5.5 Register Agent

```bash
# Update scripts/register-agent.js with IPFS hash
# Then run:
npx hardhat run scripts/register-agent.js --network baseMainnet
```

### 5.6 Verify on BaseScan

1. Go to https://basescan.org
2. Search for your contract address
3. Verify the contract source code
4. View your agent registration

---

## Phase 6: Launch Marketing (20 minutes)

### 6.1 Run Orchestrator (Dry Run)

```bash
python automation/orchestrator.py
```

This shows what will be posted without actually posting.

### 6.2 Live Launch (With API Keys)

```bash
# Set API credentials
export TWITTER_API_KEY="..."
export TWITTER_API_SECRET="..."
export TWITTER_ACCESS_TOKEN="..."
export TWITTER_ACCESS_SECRET="..."

# Run live
python automation/orchestrator.py --live
```

**What happens:**
1. 🐦 Twitter thread posted
2. 🤖 Reddit posts to 3 subreddits
3. 🐙 GitHub release created
4. 📋 MCP Registry PR drafted
5. 🌐 x402 Bazaar submission ready

---

## Phase 7: Proof of Live Agent (Verification)

### 7.1 Screenshot Checklist

Take screenshots of:
- [ ] Railway dashboard showing deployed service
- [ ] Health endpoint response (200 OK)
- [ ] Payment required response (402)
- [ ] Successful paid request (200 with results)
- [ ] BaseScan wallet showing USDC balance

### 7.2 Transaction Proof

Once you have real payments:

```bash
# Check wallet transactions on BaseScan
open https://basescan.org/address/0xb3e17988e6eE4D31e6D07decf363f736461d9e08#tokentxns

# Look for incoming USDC transfers
# Each $0.10 payment will show as a transaction
```

### 7.3 API Logs

```bash
# View Railway logs
railway logs

# Look for:
# - Incoming requests
# - Payment verifications
# - Agent responses
```

---

## Quick Reference Commands

```bash
# Deploy
./deploy.sh

# Test health
curl https://YOUR-URL.up.railway.app/health

# Test with payment
curl -X POST https://YOUR-URL.up.railway.app/find \
  -H "X-Payment-Signature: test" \
  -d '{"trade": "plumber", "location": "Austin, TX"}'

# View logs
railway logs

# Marketing dry run
python automation/orchestrator.py

# Marketing live
python automation/orchestrator.py --live
```

---

## Troubleshooting

### "OPENAI_API_KEY not set"
```bash
export OPENAI_API_KEY="sk-..."
```

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### "Health check failed"
```bash
# Check Railway logs
railway logs

# Common issues:
# - Missing .env file
# - Invalid OPENAI_API_KEY
# - Port conflict (app uses 8000)
```

### "Payment not working"
```bash
# Verify wallet has USDC
curl https://YOUR-URL.up.railway.app/payment-info
```

---

## Success Criteria

✅ **Deployment:** Agent responds to /health  
✅ **Payments:** Returns 402 without header, 200 with header  
✅ **Functionality:** Returns contractor data  
✅ **Wallet:** Shows USDC on BaseScan  
✅ **Marketing:** Posted to Twitter/Reddit  

---

## Next Steps After Launch

1. **Monitor** — Check Railway logs daily
2. **Iterate** — Add real license verification APIs
3. **Scale** — Add more data sources (Yelp, Angi)
4. **Revenue** — Track USDC incoming on BaseScan
5. **Community** — Respond to feedback on social

---

**Ready to launch? Start with Phase 1!**

Run: `cd ~/contractor-finder-agent && cat .env` to verify your setup.
