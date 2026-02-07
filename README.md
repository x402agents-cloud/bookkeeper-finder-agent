# 📚 BookkeeperFinder Agent

[![x402 Payments](https://img.shields.io/badge/x402-micropayments-blue)](https://x402.org)
[![AI Agent](https://img.shields.io/badge/AI-Agent-green)](https://github.com/x402agents-cloud/bookkeeper-finder-agent)
[![Base Network](https://img.shields.io/badge/Base-EIP--8453-0052FF)](https://base.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**An AI-powered bookkeeper discovery agent with x402 micropayment integration.** Pay $0.10 USDC per search to find vetted bookkeepers matching your specific needs.

## 🚀 Live Endpoint

**URL:** `https://autarchic-unbodied-bryson.ngrok-free.dev`

## 💰 Pricing

| Endpoint | Price | Description |
|----------|-------|-------------|
| `GET /` | Free | Service info |
| `GET /health` | Free | Health check |
| `POST /find` | $0.10 USDC | Find bookkeepers matching criteria |

## 🔧 How It Works

1. Client sends a `POST /find` request with search criteria
2. x402 middleware intercepts and requires a USDC payment on Base
3. Payment is verified via the x402 facilitator
4. AI searches for matching bookkeepers and returns results

## 📡 API Usage

```bash
# Check service info
curl https://autarchic-unbodied-bryson.ngrok-free.dev/

# Find bookkeepers (requires x402 payment header)
curl -X POST https://autarchic-unbodied-bryson.ngrok-free.dev/find \
  -H "Content-Type: application/json" \
  -H "X-PAYMENT: <x402-payment-token>" \
  -d '{"query": "QuickBooks certified bookkeeper in Miami"}'
```

## 🏗️ Tech Stack

- **Framework:** FastAPI + Uvicorn
- **Payments:** x402 v2 (EVM/Base USDC)
- **AI:** OpenAI for intelligent matching
- **Network:** Base (EIP-155:8453)

## 🔑 Wallet

`0xb3e17988e6eE4D31e6D07decf363f736461d9e08`

## 🏃 Running Locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
BASE_WALLET_ADDRESS=0xYourWallet uvicorn src.x402_integration:app --port 8402
```

## 📋 Related

- [ContractorFinder Agent](https://github.com/x402agents-cloud/contractor-finder-agent) — Find contractors with x402 payments
- [x402 Protocol](https://x402.org) — HTTP 402 Payment Required standard

---

*Built with ❤️ and x402 micropayments on Base*
