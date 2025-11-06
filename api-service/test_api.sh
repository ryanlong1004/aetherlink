#!/bin/bash
# Test script for AetherLink API

BASE_URL="http://localhost:8000"

echo "🧪 Testing AetherLink API..."
echo ""

# Health check
echo "1. Health Check"
curl -s "$BASE_URL/health" | python3 -m json.tool
echo ""

# Root endpoint
echo "2. Root Endpoint"
curl -s "$BASE_URL/" | python3 -m json.tool
echo ""

# Network status
echo "3. Network Status"
curl -s "$BASE_URL/api/network/status" | python3 -m json.tool
echo ""

# Devices
echo "4. All Devices"
curl -s "$BASE_URL/api/devices" | python3 -m json.tool
echo ""

# Stats
echo "5. Network Stats"
curl -s "$BASE_URL/api/stats" | python3 -m json.tool
echo ""

# Activities
echo "6. Recent Activities"
curl -s "$BASE_URL/api/activities?limit=5" | python3 -m json.tool
echo ""

echo "✅ Tests complete!"
