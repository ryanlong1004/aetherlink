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

## 🎨 Visual Identity

**Palette**: Deep indigo, cyan glow, brass/bronze accents (steampunk tech feel)

**Typography**:

- _Orbitron_ - Futuristic sans-serif for UI elements
- _Merriweather_ - Classic serif for headers

**UI Motif**: "Glass and metal" dashboard — translucent panels, animated gauges, glowing network nodes

**Design Elements**:

- Glassmorphism panels with backdrop blur
- Cyan (#00e5ff) and bronze (#cd7f32) color scheme
- Pulsing glow effects on active elements
- Custom scrollbars with gradient styling

---

## 🛠️ Tech Stack

- **Framework**: Nuxt 3 with Vue 3 Composition API
- **Language**: TypeScript
- **Styling**: Tailwind CSS with custom AetherLink theme
- **Charts**: Chart.js with Vue-chartjs
- **Fonts**: Google Fonts (Orbitron & Merriweather)
- **API**: Nuxt server routes

---

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ or later
- npm, yarn, pnpm, or bun

### Installation

1. Clone the repository:

```bash
git clone https://github.com/ryanlong1004/aetherlink.git
cd aetherlink
```

2. Install dependencies:

```bash
npm install
```

3. Start the development server:

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Development

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Generate static site
npm run generate
```

## Project Structure

```
aetherlink/
├── app.vue                  # Root component
├── nuxt.config.ts          # Nuxt configuration
├── assets/
│   └── css/
│       └── main.css        # Global styles
├── components/
│   ├── Dashboard.vue       # Main dashboard component
│   ├── StatsCard.vue       # Statistics card component
│   ├── NetworkChart.vue    # Network traffic chart
│   ├── DeviceList.vue      # Connected devices list
│   └── ActivityLog.vue     # Activity log component
├── pages/
│   └── index.vue           # Home page
└── server/
    └── api/
        └── network/
            └── status.ts   # Network status API endpoint
```

## API Endpoints

### GET `/api/network/status`

Returns current network status including:

- Network statistics (devices, speed, data usage, uptime)
- Connected devices list
- Recent activity log
- Network traffic chart data

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
