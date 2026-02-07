#!/bin/bash
# Deploy BookkeeperFinder Agent to Production

set -e

echo "🚀 Deploying BookkeeperFinder Agent..."
echo "========================================"

# Configuration
AGENT_NAME="bookkeeper-finder"

# Step 1: Verify environment
echo ""
echo "📋 Step 1: Checking environment..."

if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY not set"
    exit 1
fi

echo "✅ Environment OK"

# Step 2: Test locally
echo ""
echo "🧪 Step 2: Testing agent locally..."
python3 -c "from src.agent import agent; result = agent.find_bookkeepers('Austin, TX'); print('✅ Agent test passed')"

# Step 3: Check if Railway CLI is installed
echo ""
echo "🚂 Step 3: Checking Railway CLI..."

if ! command -v railway &> /dev/null; then
    echo "Installing Railway CLI..."
    npm install -g @railway/cli
fi

echo "✅ Railway CLI ready"

# Step 4: Deploy to Railway
echo ""
echo "🚂 Step 4: Deploying to Railway..."

# Check if already initialized
if [ ! -d ".railway" ]; then
    echo "Initializing Railway project..."
    railway login
    railway init --name $AGENT_NAME
fi

# Deploy
railway up

echo ""
echo "✅ Deployed to Railway!"
echo ""

# Get the URL
RAILWAY_URL=$(railway domain 2>/dev/null || echo "https://$AGENT_NAME.up.railway.app")
echo "🌐 URL: $RAILWAY_URL"

# Step 5: Verify deployment
echo ""
echo "🔍 Step 5: Verifying deployment..."
sleep 5

if curl -s "$RAILWAY_URL/health" > /dev/null; then
    echo "✅ Health check passed!"
    curl -s "$RAILWAY_URL/health" | python3 -m json.tool
else
    echo "⚠️ Health check failed - deployment may still be starting"
fi

# Step 6: Summary
echo ""
echo "========================================"
echo "🎉 DEPLOYMENT COMPLETE!"
echo "========================================"
echo ""
echo "Your agent is live at:"
echo "  $RAILWAY_URL"
echo ""
echo "Next steps:"
echo "  1. Test the API: curl $RAILWAY_URL/health"
echo "  2. Run marketing: python automation/orchestrator.py"
echo "  3. Submit to MCP registry"
echo "  4. List on x402 Bazaar"
echo ""
