# 🌐 AetherLink

<div align="center">
  <img src="public/logo.png" alt="AetherLink Logo" width="200"/>
  
  ### *See the unseen. Control the connected.*
  
  **Your home network, visualized.**

![Status](https://img.shields.io/badge/Status-Active-00e5ff) ![Vue 3](https://img.shields.io/badge/Vue-3.x-00e5ff) ![Nuxt 3](https://img.shields.io/badge/Nuxt-3.x-cd7f32) ![TypeScript](https://img.shields.io/badge/TypeScript-5.x-00e5ff)

</div>

---

## 🧭 Concept

**AetherLink** is a web-based dashboard for monitoring and visualizing your home wireless network. It brings together **real-time device status**, **historical trends**, **interactive visualizations**, and **network activity tracking** — turning the invisible wireless world into clear visual insight.

The name draws from _"aether,"_ the invisible medium through which signals travel, and _"link,"_ the connections between devices.

### Taglines

- _"See the unseen. Control the connected."_
- _"Your home network, visualized."_
- _"The pulse of your wireless world."_
- _"From signal to sense."_
- _"Link the invisible."_

---

## ✨ Features

- � **Real-time Network Statistics** - Monitor connected devices, network speed, data usage, and uptime
- 📈 **Traffic Analytics** - Visualize network traffic with interactive Chart.js visualizations
- 🔌 **Device Management** - Track all connected devices with live status indicators
- 📝 **Activity Logging** - Keep tabs on network events and device activities
- 🎨 **Steampunk-Futuristic UI** - Glass and metal aesthetic with cyan glow and bronze accents
- ⚡ **Live Updates** - Auto-refreshing data every 30 seconds
- 🌊 **Animated Components** - Pulse effects, glowing nodes, and smooth transitions

---

## 🛠️ Tech Stack

### Frontend

- **Framework**: Nuxt 3 with Vue 3 Composition API
- **Language**: TypeScript
- **Styling**: Tailwind CSS with custom AetherLink theme
- **Charts**: Chart.js with Vue-chartjs
- **Fonts**: Google Fonts (Orbitron & Merriweather)

### Backend

- **Framework**: FastAPI (Python 3.12)
- **Network Monitoring**: psutil, subprocess (ARP scanning)
- **API Documentation**: Swagger UI / ReDoc (auto-generated)

### Deployment

- **Containers**: Docker & Docker Compose
- **Architecture**: Microservices (separate API and frontend)

---

## 🚀 Getting Started

### Quick Start with Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/ryanlong1004/aetherlink.git
cd aetherlink

# Start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### Development Setup

#### API Service (Python/FastAPI)

```bash
cd api-service

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
./start.sh
# Or manually:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# API will be available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

#### Frontend (Nuxt 3)

```bash
# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env and set NUXT_PUBLIC_API_BASE=http://localhost:8000

# Start development server
npm run dev

# Frontend will be available at http://localhost:3000
```

## Project Structure

```
aetherlink/
├── api-service/              # Python FastAPI backend
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   ├── models/          # Pydantic models
│   │   │   └── network.py   # Network data models
│   │   ├── routers/         # API route handlers
│   │   │   └── network.py   # Network endpoints
│   │   └── services/        # Business logic
│   │       └── network_monitor.py  # Network scanning service
│   ├── Dockerfile           # API container config
│   ├── requirements.txt     # Python dependencies
│   ├── start.sh            # Development startup script
│   └── test_api.sh         # API testing script
├── components/              # Vue components
│   ├── Dashboard.vue       # Main dashboard
│   ├── StatsCard.vue       # Statistics cards
│   ├── NetworkChart.vue    # Traffic visualization
│   ├── DeviceList.vue      # Device listing
│   └── ActivityLog.vue     # Activity feed
├── pages/
│   └── index.vue           # Home page
├── assets/
│   └── css/
│       └── main.css        # Global styles & animations
├── public/
│   └── logo.png           # AetherLink logo
├── Dockerfile             # Frontend container config
├── docker-compose.yml     # Multi-container orchestration
├── nuxt.config.ts        # Nuxt configuration
├── tailwind.config.ts    # Tailwind customization
└── package.json
```

## API Endpoints

### Base URL: `http://localhost:8000`

#### Network Monitoring

- `GET /api/network/status` - Complete network status (devices, stats, activities, chart data)
- `GET /api/devices` - List all connected devices
- `GET /api/devices/{device_id}` - Get specific device details
- `GET /api/stats` - Network statistics (speed, uptime, data usage)
- `GET /api/activities?limit=10` - Recent network activities

#### System

- `GET /` - API information
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)

### Response Models

All endpoints return JSON with proper typing via Pydantic models. See the interactive documentation at `/docs` for detailed schemas and example requests.

---

## 🔌 Using Real Network Data

By default, AetherLink uses mock data for demonstration. To monitor your actual home network:

### Quick Setup

1. **Copy environment file:**

   ```bash
   cp .env.example .env
   ```

2. **Enable real data mode** in `.env`:

   ```env
   USE_REAL_NETWORK_DATA=true
   NETWORK_PREFIX=192.168.1  # Your network prefix
   ```

3. **Run with permissions:**

   ```bash
   # Linux/Mac - may need sudo for network access
   sudo npm run dev

   # Or grant node capabilities (Linux):
   sudo setcap cap_net_raw+eip $(which node)
   npm run dev
   ```

4. **Visit** `http://localhost:3000` to see your real network devices!

### What You'll See

- ✅ All connected devices on your network
- ✅ Real-time network speed and data usage
- ✅ System uptime
- ✅ Device types and MAC addresses
- ✅ Network activity tracking

### Advanced Integration

For detailed metrics, integrate with your router's API:

- **UniFi Controller** - Install `node-unifi`
- **ASUS Router** - Install `asuswrt`
- **TP-Link** - Install `tp-link-cloud-api`
- **SNMP** - Install `net-snmp` for enterprise routers

📖 **[Read the complete integration guide](docs/REAL_DATA_GUIDE.md)** for router-specific setup, troubleshooting, and advanced options.

---

## Customization

- Connected devices list
- Recent activity log
- Network traffic chart data

## Customization

### Adding Real Network Monitoring

The current implementation uses mock data. To integrate with real network monitoring:

1. Install network monitoring libraries (e.g., `node-arp`, `network`)
2. Update `/server/api/network/status.ts` to fetch real network data
3. Consider adding router API integration for more detailed metrics

### Styling

Modify `assets/css/main.css` and Tailwind configuration in `nuxt.config.ts` to customize the appearance.

## Roadmap

- [ ] Real-time WebSocket updates for instant network changes
- [ ] Individual device bandwidth monitoring
- [ ] Historical data storage with trend analysis
- [ ] Router API integration (SNMP, UPnP)
- [ ] Mobile responsive improvements
- [ ] Dark/light theme toggle with preference persistence
- [ ] Device blocking/management capabilities
- [ ] Network security alerts and notifications
- [ ] Customizable dashboard layouts
- [ ] Export network reports (PDF/CSV)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Acknowledgments

- Built with [Nuxt 3](https://nuxt.com/)
- Charts powered by [Chart.js](https://www.chartjs.org/)
- Styled with [Tailwind CSS](https://tailwindcss.com/)
