#!/bin/bash
# Test script for enhanced AetherLink API with extensive data collection

API_BASE="http://localhost:8000/api"
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     AetherLink API - Enhanced Features Test Suite       ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# 1. Test Diagnostics
echo -e "${YELLOW}1. Service Diagnostics:${NC}"
curl -s "${API_BASE}/diagnostics" | python3 -m json.tool
echo ""

# 2. Test Network Status (comprehensive)
echo -e "${YELLOW}2. Complete Network Status:${NC}"
echo -e "   ${GREEN}Stats:${NC}"
curl -s "${API_BASE}/network/status" | python3 -c "
import sys, json
d = json.load(sys.stdin)
s = d['stats']
print(f\"   Connected Devices: {s['connected_devices']}\")
print(f\"   Network Speed: {s['network_speed']} Mbps\")
print(f\"   Data Usage: {s['data_usage']} GB\")
print(f\"   Uptime: {s['uptime']}\")
"
echo ""

# 3. Test Device List
echo -e "${YELLOW}3. Connected Devices (showing first 3):${NC}"
curl -s "${API_BASE}/devices" | python3 -c "
import sys, json
devices = json.load(sys.stdin)[:3]
for d in devices:
    vendor = f\" ({d['vendor']})\" if d['vendor'] else \"\"
    print(f\"   • {d['name']}{vendor} - {d['ip']} [{d['type']}]\")
"
echo ""

# 4. Test Activities
echo -e "${YELLOW}4. Recent Network Activities (last 5):${NC}"
curl -s "${API_BASE}/activities?limit=5" | python3 -c "
import sys, json
activities = json.load(sys.stdin)
for a in activities:
    print(f\"   • {a['device']}: {a['action']}\")
"
echo ""

# 5. Test Caching
echo -e "${YELLOW}5. Caching Test:${NC}"
echo "   First call (will scan)..."
START=$(date +%s%3N)
curl -s "${API_BASE}/devices" > /dev/null
END=$(date +%s%3N)
FIRST_TIME=$((END - START))
echo "   Time: ${FIRST_TIME}ms"

echo "   Second call (should be cached)..."
START=$(date +%s%3N)
curl -s "${API_BASE}/devices" > /dev/null
END=$(date +%s%3N)
SECOND_TIME=$((END - START))
echo "   Time: ${SECOND_TIME}ms"
echo "   Speed improvement: $((FIRST_TIME - SECOND_TIME))ms faster"
echo ""

# 6. Test Historical Data
echo -e "${YELLOW}6. Historical Data Collection:${NC}"
curl -s "${API_BASE}/diagnostics" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"   Network History: {d['network_history_count']} snapshots\")
print(f\"   Stats History: {d['stats_history_count']} readings\")
print(f\"   Total Activities: {d['activity_count']} events\")
print(f\"   Cache Age: {d['cache_age_seconds']:.2f}s (valid: {d['cache_valid']})\")
"
echo ""

# 7. Test Chart Data
echo -e "${YELLOW}7. Chart Data (using real network stats):${NC}"
curl -s "${API_BASE}/network/status" | python3 -c "
import sys, json
d = json.load(sys.stdin)
chart = d['chart_data'][-5:] if len(d['chart_data']) > 0 else []
print(f\"   Available data points: {len(d['chart_data'])}\")
if chart:
    print(\"   Recent measurements:\")
    for c in chart:
        print(f\"     {c['time']}: ↓{c['download']} Mbps / ↑{c['upload']} Mbps\")
"
echo ""

# 8. Test Multiple Scans for Speed Calculation
echo -e "${YELLOW}8. Real-time Speed Calculation (3 samples):${NC}"
for i in {1..3}; do
    sleep 2
    curl -s "${API_BASE}/stats" | python3 -c "
import sys, json
s = json.load(sys.stdin)
print(f\"   Sample ${i}: {s['network_speed']} Mbps\")
"
done
echo ""

echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    Test Complete!                        ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
