# Aetherlink 🌐

A modern web-based dashboard for monitoring your home wireless network with real-time device tracking, network analytics, and activity logs.

![Aetherlink Dashboard](https://img.shields.io/badge/Status-Active-green) ![Vue 3](https://img.shields.io/badge/Vue-3.x-brightgreen) ![Nuxt 3](https://img.shields.io/badge/Nuxt-3.x-00DC82) ![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue)

## Features

- 📊 **Real-time Network Statistics** - Monitor connected devices, network speed, data usage, and uptime
- 📈 **Traffic Analytics** - Visualize network traffic with interactive charts
- 🔌 **Device Management** - Track all connected devices with status indicators
- 📝 **Activity Logging** - Keep tabs on network events and device activities
- 🎨 **Modern UI** - Beautiful gradient design with glassmorphism effects
- ⚡ **Live Updates** - Auto-refreshing data every 30 seconds

## Tech Stack

- **Framework**: Nuxt 3 with Vue 3
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Chart.js with Vue-chartjs
- **API**: Nuxt server routes

## Getting Started

### Prerequisites

- Node.js 18+ or later
- npm, yarn, pnpm, or bun

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/aetherlink.git
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

## Customization

### Adding Real Network Monitoring

The current implementation uses mock data. To integrate with real network monitoring:

1. Install network monitoring libraries (e.g., `node-arp`, `network`)
2. Update `/server/api/network/status.ts` to fetch real network data
3. Consider adding router API integration for more detailed metrics

### Styling

Modify `assets/css/main.css` and Tailwind configuration in `nuxt.config.ts` to customize the appearance.

## Roadmap

- [ ] Real-time WebSocket updates
- [ ] Device bandwidth monitoring
- [ ] Historical data storage
- [ ] Router integration
- [ ] Mobile responsive improvements
- [ ] Dark/light theme toggle
- [ ] Device blocking/management
- [ ] Network security alerts

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Acknowledgments

- Built with [Nuxt 3](https://nuxt.com/)
- Charts powered by [Chart.js](https://www.chartjs.org/)
- Styled with [Tailwind CSS](https://tailwindcss.com/)
