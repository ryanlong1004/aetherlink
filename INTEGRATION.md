# AetherLink - Integration Guide

## 🔗 API + Dashboard Integration

The AetherLink dashboard is now fully integrated with the enhanced FastAPI backend, displaying real-time network data with extensive metrics.

## Architecture

```
┌─────────────────────┐         ┌──────────────────────┐
│   Nuxt Frontend     │         │   FastAPI Backend    │
│   (Port 3000)       │ ◄─────► │   (Port 8000)        │
│                     │  HTTP   │                      │
│  - Dashboard UI     │         │  - ARP Scanning      │
│  - Device List      │         │  - Vendor Database   │
│  - Network Chart    │         │  - Quality Metrics   │
│  - Activity Log     │         │  - Historical Data   │
└─────────────────────┘         └──────────────────────┘
```

## Quick Start

### 1. Start the API Service

```bash
cd api-service
source ../.venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. Start the Frontend

```bash
# In project root
npm run dev
```

### 3. Access the Dashboard

Open http://localhost:3000 in your browser

## Environment Configuration

Create `.env` in project root:

```bash
# API endpoint
NUXT_PUBLIC_API_BASE=http://localhost:8000
```

## Features Displayed

### Stats Cards
- **Connected Devices**: Live count from API
- **Network Speed**: Real-time Mbps calculation
- **Data Usage**: Total GB transferred
- **Uptime**: System uptime

### Device List (Enhanced!)
Each device now shows:
- 📱 Device icon based on type
- Device name (with vendor if identified)
- IP address
- Connection status badge
- **⚡ Latency** (ms) - NEW!
- **📶 Packet loss** (%) - NEW!
- **Connection quality badge** (excellent/good/fair/poor) - NEW!
- **🔄 Total connections** - NEW!

Quality badge colors:
- 🟢 **Excellent**: <10ms, <5% loss (green)
- 🔵 **Good**: 10-50ms, <5% loss (blue)
- 🟡 **Fair**: 50-100ms or 5-10% loss (yellow)
- 🔴 **Poor**: >100ms or >10% loss (red)

### Network Chart
- Real-time bandwidth visualization
- Download/Upload speeds over time
- Historical data from API

### Activity Log
- Device connections
- Device disconnections
- IP address changes
- Real-time event updates

## API Endpoints Used

The dashboard calls these API endpoints:

### Primary Endpoint
```
GET /api/network/status
```
Returns complete network status:
- Statistics (devices, speed, usage, uptime)
- All connected devices with full metrics
- Recent activities
- Chart data for visualization

### Response Example
```json
{
  "stats": {
    "connected_devices": 19,
    "network_speed": 1.65,
    "data_usage": 131.6,
    "uptime": "48d 0h"
  },
  "devices": [
    {
      "id": "54af978460a0",
      "name": "Device 11",
      "ip": "192.168.1.11",
      "mac": "54:af:97:84:60:a0",
      "status": "online",
      "type": "default",
      "vendor": null,
      "last_seen": "2025-11-06T19:47:19.980100",
      "latency": 13.347,
      "packet_loss": 0.0,
      "connection_quality": "good",
      "first_seen": "2025-11-06T19:47:19.980100",
      "total_connections": 1
    }
  ],
  "activities": [...],
  "chart_data": [...]
}
```

## Data Refresh

- **Auto-refresh**: Every 30 seconds
- **Caching**: API caches scans for 5 seconds
- **Performance**: ~5-10ms for cached requests

## Troubleshooting

### Dashboard shows mock data
- Ensure API is running on port 8000
- Check `.env` has correct `NUXT_PUBLIC_API_BASE`
- Check browser console for API errors

### API not accessible
```bash
# Verify API is running
curl http://localhost:8000/api/diagnostics

# Should return service diagnostics
```

### No connection quality metrics
- Connection quality is measured selectively (every 5th device)
- Quality data accumulates over time
- Refresh the page after a few scans

## Development Tips

### Watch API logs
```bash
# In api-service directory
tail -f api.log
```

### Test API manually
```bash
# Get full status
curl http://localhost:8000/api/network/status | jq

# Get diagnostics
curl http://localhost:8000/api/diagnostics | jq

# Get devices only
curl http://localhost:8000/api/devices | jq
```

### Frontend dev mode
- Hot reload enabled
- Changes reflect immediately
- Check browser console for errors

## Docker Deployment

### Build and run with Docker Compose

```bash
docker-compose up --build
```

Services:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Production Considerations

1. **Environment Variables**
   - Set `NUXT_PUBLIC_API_BASE` to production API URL
   - Use HTTPS in production

2. **CORS**
   - API already configured for CORS
   - Update allowed origins for production

3. **Caching**
   - 5-second cache appropriate for home networks
   - Adjust `cache_duration` in `network_monitor.py` if needed

4. **Monitoring**
   - Use `/api/diagnostics` for health checks
   - Monitor cache hit rate
   - Track historical data accumulation

---

**Status**: ✅ Fully Integrated  
**Frontend**: Nuxt 3 @ http://localhost:3000  
**Backend**: FastAPI @ http://localhost:8000  
**Documentation**: http://localhost:8000/docs
