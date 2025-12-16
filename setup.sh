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
sleep 15

# Check container health
echo "🔍 Checking service health..."
docker compose ps

# Wait for EDC to be fully ready
echo "⏳ Waiting for EDC services to initialize..."
sleep 15

# Initialize provider with sample data
echo "🔧 Initializing provider with sample data..."

echo ""
echo "✅ EDC Simple UI Setup Complete!"
echo ""
echo "🔗 Services (Minimal):"
echo "   EDC Connector:           http://localhost:19193"
echo "   Data Server:             http://localhost:8000"
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