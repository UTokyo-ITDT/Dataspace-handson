#!/bin/bash

# EDC Simple UI - Minimal Setup
# =============================
# This script starts only the essential services for EDC Simple UI

set -e

echo "🚀 Starting EDC Simple UI (Minimal Setup)..."

# Start minimal EDC services
echo "📦 Starting essential EDC services..."
docker compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to start up..."
sleep 60

# Check container health
echo "🔍 Checking service health..."
docker compose ps

# Wait for EDC to be fully ready
echo "⏳ Waiting for EDC services to initialize..."
sleep 30

# Initialize provider with sample data
echo "🔧 Initializing provider with sample data..."

# Create sample asset
echo "📦 Creating sample asset..."
curl -s -X POST http://edc-connector:19193/management/v3/assets \
  -H 'Content-Type: application/json' \
  --data-binary @resources/create-asset.json > /dev/null && echo "✅ Asset created" || echo "⚠️  Asset creation failed or already exists"

# Create sample policy
echo "📋 Creating sample policy..."
curl -s -X POST http://edc-connector:19193/management/v3/policydefinitions \
  -H 'Content-Type: application/json' \
  --data-binary @resources/create-policy.json > /dev/null && echo "✅ Policy created" || echo "⚠️  Policy creation failed or already exists"

# Create sample contract definition
echo "📄 Creating sample contract definition..."
curl -s -X POST http://edc-connector:19193/management/v3/contractdefinitions \
  -H 'Content-Type: application/json' \
  --data-binary @resources/create-contract-definition.json > /dev/null && echo "✅ Contract definition created" || echo "⚠️  Contract definition creation failed or already exists"

echo ""
echo "✅ EDC Simple UI Setup Complete!"
echo ""
echo "🔗 Services (Minimal):"
echo "   EDC Connector:           http://localhost:19193"
echo "   Data Server:             http://localhost:7080"
echo "   EDC Simple UI:           http://localhost:8501"
echo ""
echo "🎯 Ready to use:"
echo "   🌐 Open: http://localhost:8501"
echo "   🔄 Test all EDC operations through the web interface"
echo ""
echo "🛠️  Container Management:"
echo "   📋 View logs: docker compose logs -f"
echo "   🛑 Stop all:  docker compose down"
echo "   🔄 Restart:   docker compose restart"
echo ""